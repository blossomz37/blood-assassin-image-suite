(() => {
  const $ = (sel) => document.querySelector(sel);
  const form = $('#genForm');
  const statusEl = $('#status');
  const results = $('#results');
  const promptFileInput = $('#prompt_file');
  const promptTextarea = $('#prompt');
  const nameInput = $('#name');
  const apiKeyInput = $('#apiKey');

  // If user selects a file, try to fill textarea with its contents (for visibility)
  promptFileInput.addEventListener('change', async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      if (text && !promptTextarea.value) {
        promptTextarea.value = text;
      }
      if (!nameInput.value) {
        const stem = file.name.replace(/\.[^.]+$/, '');
        nameInput.value = stem;
      }
    } catch {}
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    results.innerHTML = '';
    setStatus('Generating…');

    const useMultipart = promptFileInput.files && promptFileInput.files.length > 0;
    let resp;
    try {
      if (useMultipart) {
        const fd = new FormData();
        if (nameInput.value.trim()) fd.set('name', nameInput.value.trim());
        if (promptTextarea.value.trim()) fd.set('prompt', promptTextarea.value.trim());
        fd.set('prompt_file', promptFileInput.files[0]);
        if (apiKeyInput.value.trim()) fd.set('apiKey', apiKeyInput.value.trim());
        resp = await fetch('/api/generate', { method: 'POST', body: fd });
      } else {
        const body = {
          name: nameInput.value.trim() || undefined,
          prompt: promptTextarea.value.trim(),
          apiKey: apiKeyInput.value.trim() || undefined,
        };
        resp = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
      }
    } catch (err) {
      setStatus('Network error. See console.');
      console.error(err);
      return;
    }

    let data;
    try {
      data = await resp.json();
    } catch {
      setStatus('Invalid server response');
      return;
    }

    if (!resp.ok) {
      setStatus(data?.error || 'Generation failed');
      return;
    }

    setStatus(`Done. ${data.images.length} image(s).`);
    renderResults(data.urls || [], data.images || []);
  });

  function setStatus(msg) {
    statusEl.textContent = msg || '';
  }

  function renderResults(urls, filenames) {
    if (!urls.length) {
      results.innerHTML = '<p>No images returned.</p>';
      return;
    }
    const frag = document.createDocumentFragment();
    urls.forEach((url, i) => {
      const card = document.createElement('div');
      card.className = 'imgCard';

      const img = document.createElement('img');
      img.src = url;
      img.alt = filenames[i] || `image_${i+1}`;

      const actions = document.createElement('div');
      actions.className = 'imgActions';

      const dl = document.createElement('a');
      dl.href = url;
      dl.download = filenames[i] || '';
      dl.textContent = 'Download';

      const open = document.createElement('a');
      open.href = url;
      open.target = '_blank';
      open.rel = 'noopener noreferrer';
      open.textContent = 'Open';

      actions.append(dl, open);
      card.append(img, actions);
      frag.append(card);
    });
    results.innerHTML = '';
    results.append(frag);
  }
})();
