function buble(title, message, img = 'https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif') {
    let AlertTemplate = document.createElement('div');

    AlertTemplate.setAttribute('onclick', "this.remove()");
    AlertTemplate.className = 'alert shadow-lg';

    AlertTemplate.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-info shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
    <div>
      <h3 class="font-bold">${title}</h3>
      <div class="text-xs">${message}</div>
    </div>
    `;
    
    document.getElementById('toast').append(AlertTemplate);
    setTimeout(() => {AlertTemplate.remove()}, 3000);

};