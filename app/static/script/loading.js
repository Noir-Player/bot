const spinner = document.createElement('span');
spinner.setAttribute('class', 'loading loading-spinner loading-xs');
spinner.setAttribute('role', 'status');
spinner.setAttribute('aria-hidden', 'true');

function loading(label, element) {
    element.innerHTML = `${label} `;
    element.appendChild(spinner);
    element.disabled = true;
    element.onclick = null;
  };