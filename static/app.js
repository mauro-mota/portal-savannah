(() => {
 const menus = [...document.querySelectorAll('.account-menu, .mobile-nav')];
 menus.forEach(menu => menu.addEventListener('toggle', () => {if(menu.open)menus.forEach(other=>{if(other!==menu)other.open=false;});}));
 document.addEventListener('keydown', e => {if(e.key==='Escape')menus.forEach(menu=>{if(menu.open){menu.open=false;menu.querySelector('summary').focus();}});});
 document.addEventListener('click', e => menus.forEach(menu=>{if(menu.open&&!menu.contains(e.target))menu.open=false;}));
 document.querySelectorAll('[data-password]').forEach(button=>{const field=document.getElementById(button.dataset.password);if(!field)return;button.hidden=false;button.addEventListener('click',()=>{const show=field.type==='password';field.type=show?'text':'password';button.textContent=show?'Ocultar':'Mostrar';button.setAttribute('aria-pressed',String(show));});});
})();
