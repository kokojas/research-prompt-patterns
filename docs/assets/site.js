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

// Content stays visible with no JS. Motion is a progressive, one-time enhancement.
(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reducedMotion.matches || !('IntersectionObserver' in window) || !Element.prototype.animate) return;
  const running = new Set();
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      if (reducedMotion.matches) return;
      const animation = entry.target.animate(
        [{ opacity: 0, transform: 'translateY(10px)' }, { opacity: 1, transform: 'translateY(0)' }],
        { duration: 480, easing: 'cubic-bezier(.2,.65,.25,1)' }
      );
      running.add(animation);
      animation.finished.then(() => running.delete(animation)).catch(() => running.delete(animation));
    });
  }, { threshold: .08 });
  document.querySelectorAll('[data-reveal]').forEach(element => observer.observe(element));
  reducedMotion.addEventListener('change', event => {
    if (!event.matches) return;
    observer.disconnect();
    running.forEach(animation => animation.cancel());
    running.clear();
  });
})();

// Make scrollable prompt text accessible to keyboard users and announce copy feedback.
document.querySelectorAll('.prompt-code').forEach(element => {
  element.tabIndex = 0;
  element.setAttribute('aria-label', document.documentElement.lang === 'uk' ? 'Текст промпту' : 'Prompt text');
});
document.querySelectorAll('[data-copy-target]').forEach(button => {
  button.setAttribute('aria-live', 'polite');
  button.setAttribute('aria-atomic', 'true');
});
