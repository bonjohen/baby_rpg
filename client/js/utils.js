/* DOM & utility helpers */

function el(tag, attrs, ...children) {
    const e = document.createElement(tag);
    if (attrs) {
        for (const [k, v] of Object.entries(attrs)) {
            if (k === 'className') e.className = v;
            else if (k === 'textContent') e.textContent = v;
            else if (k === 'innerHTML') e.innerHTML = v;
            else if (k.startsWith('on')) e.addEventListener(k.slice(2).toLowerCase(), v);
            else e.setAttribute(k, v);
        }
    }
    for (const child of children) {
        if (typeof child === 'string') e.appendChild(document.createTextNode(child));
        else if (child) e.appendChild(child);
    }
    return e;
}

function show(element) { element.classList.remove('hidden'); }
function hide(element) { element.classList.add('hidden'); }

function showToast(message) {
    const area = document.getElementById('toast-area');
    const toast = el('div', { className: 'toast', textContent: message });
    area.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
}

function clearChildren(element) {
    while (element.firstChild) element.removeChild(element.firstChild);
}
