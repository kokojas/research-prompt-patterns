document.querySelectorAll('[data-copy-target]').forEach(button=>{
  button.addEventListener('click',async()=>{
    const target=document.getElementById(button.dataset.copyTarget);
    if(!target)return;
    const original=button.textContent;
    try{
      await navigator.clipboard.writeText(target.textContent.trim());
      button.textContent=document.documentElement.lang==='uk'?'Скопійовано':'Copied';
      window.setTimeout(()=>{button.textContent=original},1800);
    }catch{
      const selection=window.getSelection();
      const range=document.createRange();range.selectNodeContents(target);
      selection.removeAllRanges();selection.addRange(range);
      button.textContent=document.documentElement.lang==='uk'?'Виділіть і скопіюйте':'Select and copy';
    }
  });
});
