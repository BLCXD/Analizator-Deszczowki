
console.log('Main JavaScript loaded');

function testJS() {
    alert('Main JavaScript is working!');
    return true;
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    testJS();
});