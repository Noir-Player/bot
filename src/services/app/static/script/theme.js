// Не распространяется в открытом доступе

// Функция для изменения яркости цвета
function colorBrightness(color, percent, returnHex = true) {
  // Преобразуем цвет в RGB
  const rgb = hexToRgb(color);
  
  // Изменяем яркость цвета
  const updatedRgb = {
    r: rgb.r + (percent/100) * 255,
    g: rgb.g + (percent/100) * 255,
    b: rgb.b + (percent/100) * 255
  };

  // Исключение для отрицательных значений
  for (let key in updatedRgb) {
  if (updatedRgb[key] < 50) {
    updatedRgb[key] = 50;
  } else if (updatedRgb[key] > 210) {
    updatedRgb[key] = 210;
  };
};
  
  // Преобразуем обратно в HEX
  if (returnHex) {
    return rgbToHex(updatedRgb.r, updatedRgb.g, updatedRgb.b);
  } else {
    return color;
  };

}

// Функция для преобразования HEX в RGB
function hexToRgb(hex) {
  const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
  hex = hex.replace(shorthandRegex, (m, r, g, b) => {
    return r + r + g + g + b + b;
  });
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

// Функция для преобразования RGB в HEX
function rgbToHex(r, g, b) {
  return "#" + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
}


function setTheme(colorValue) {

  // SET THEME
  // set body
  document.documentElement.style.setProperty('--bs-body-bg', colorBrightness(colorValue, -70));
  document.documentElement.style.setProperty('--bs-body-color', '#fff');
  document.documentElement.style.setProperty('--bs-code-color', colorBrightness(colorValue, 0));


  //set bg value
  document.documentElement.style.setProperty('--bs-light', colorBrightness(colorValue, 20));
  document.documentElement.style.setProperty('--bs-dark', colorBrightness(colorValue, -30));
  document.documentElement.style.setProperty('--bs-primary', colorValue);

  //set button NOT WORKING
  //colors
  // document.documentElement.style.setProperty('--bs-btn-color', '#fff');
  // document.documentElement.style.setProperty('--bs-btn-hover-color', '#fff');
  // document.documentElement.style.setProperty('--bs-btn-active-color', '#fff');
  // document.documentElement.style.setProperty('--bs-btn-disabled-color', '#fff');
  // //borders
  // document.documentElement.style.setProperty('--bs-btn-border-color', '#fff');
  // document.documentElement.style.setProperty('--bs-btn-hover-border-color', '#fff');
  // document.documentElement.style.setProperty('--bs-btn-active-border-color', '#fff');
  // document.documentElement.style.setProperty('--bs-btn-disabled-border-color', '#fff');
  // //bgs
  // document.documentElement.style.setProperty('--bs-btn-bg', colorBrightness(colorValue, -30));
  // document.documentElement.style.setProperty('--bs-btn-hover-bg', colorBrightness(colorValue, 0));
  // document.documentElement.style.setProperty('--bs-btn-active-bg', colorBrightness(colorValue, 0));
  // document.documentElement.style.setProperty('--bs-btn-disabled-bg', colorBrightness(colorValue, -30));
};