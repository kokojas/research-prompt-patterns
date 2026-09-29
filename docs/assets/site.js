document.querySelectorAll('[data-copy-target]').forEach(button => {
  button.addEventListener('click', async () => {
    const target = document.getElementById(button.dataset.copyTarget);
    if (!target) return;
    const text = target.textContent.trim();
    const original = button.textContent;
    let copied = false;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await Promise.race([
          navigator.clipboard.writeText(text),
          new Promise((_, reject) => window.setTimeout(() => reject(new Error('clipboard timeout')), 1200))
        ]);
        copied = true;
      } catch { /* Try the selection fallback below. */ }
    }
    if (!copied) {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(target);
      selection.removeAllRanges();
      selection.addRange(range);
      copied = document.execCommand('copy');
    }
    button.textContent = copied
      ? (document.documentElement.lang === 'uk' ? 'Скопійовано' : 'Copied')
      : (document.documentElement.lang === 'uk' ? 'Виділіть і скопіюйте' : 'Select and copy');
    window.setTimeout(() => { button.textContent = original; }, 1800);
  });
});
