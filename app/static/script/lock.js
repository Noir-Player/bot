//This file created for load default components in pages

//load bootstrap theme
bootstrap       = document.createElement('link');
bootstrap.rel   = 'stylesheet';
bootstrap.type  = 'text/css';
bootstrap.href  = '/static/css/bootstrap.css';
      document.head.appendChild(bootstrap);


//load main theme & fonts
defaultstyle       = document.createElement('link');
defaultstyle.rel   = 'stylesheet';
defaultstyle.type  = 'text/css';
defaultstyle.href  = '/static/css/lock.css';
      document.head.appendChild(defaultstyle);


//load main icon for pages
icon      = document.createElement('link');
icon.rel  = 'icon';
icon.type = 'image/png';
icon.href = '/static/image/icon.png';  
      document.head.appendChild(icon);


//favicon for web-agent
favicon      = document.createElement('link');
favicon.rel  = 'icon';
favicon.type = 'image/x-icon';
favicon.href = '/static/image/icon.png';  
      document.head.appendChild(icon);
      
//   <----MAIN SCRIPTS---->

//Jquery
jquery     = document.createElement('script');
jquery.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
      document.head.appendChild(jquery);


//for bootstrap

popper     = document.createElement('script');
popper.src = 'https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.5/dist/umd/popper.min.js';
      document.head.appendChild(popper);


   
bootstrap.min     = document.createElement('script');
bootstrap.min.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-beta1/dist/js/bootstrap.min.js';
      document.head.appendChild(bootstrap.min);



// bundle     = document.createElement('script');
// bundle.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js';
//       document.head.appendChild(bundle);