// LEDs 1, 2 y 3
function toggleLED(ledNum) {
    fetch('/toggle?led=' + ledNum)
        .then(response => response.text())
        .then(text => {
            console.log(text);
            alert(text);
        })
        .catch(err => console.error('Error toggle LED:', err));
}

// Tira WS2812B
function changeStripColor() {
    const colorInput = document.getElementById('ledColor');
    let color = colorInput.value; 
    if (color.startsWith('#')) {
        color = color.substring(1);
    }
  
        }
