const spinnerWrapperElement =document.querySelector('.spinner-wrapper')

window.addEventListener('load', () => {
    spinnerWrapperElement.style.opacity = '0';

    setTimeout(() => {
        spinnerWrapperElement.style.display = 'none';
    }, 200);
});