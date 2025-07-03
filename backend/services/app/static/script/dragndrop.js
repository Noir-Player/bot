  function handleDragStart(e) {
      this.style.opacity = '0.4';
    
      dragSrcEl = this;
    
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/html', this.innerHTML);
    }

  function handleDragEnd(e) {
    this.style.opacity = '1';

    items.forEach(function (item) {
      item.classList.remove('bg-primary');
    });
  }

  function handleDragOver(e) {
    if (e.preventDefault) {
      e.preventDefault();
    }

    return false;
  }

  function handleDrop(e) {
      e.stopPropagation();

      if (dragSrcEl !== this) {
        document.getElementById('tracks_table').insertBefore(dragSrcEl, this);
      };

      if (window.location.pathname.startsWith('/playlists/')) {
        apiplaylists.move_track(uuid, dragSrcEl.getAttribute('id').replace('track_', ''), dragSrcEl.rowIndex);
      } else {
        apistars.move_track(dragSrcEl.getAttribute('id').replace('track_', ''), dragSrcEl.rowIndex);
      };

      return false;
  }

  items = document.querySelectorAll('.tracks_container .track');
  items.forEach(function(item) {
    item.addEventListener('dragstart', handleDragStart);
    item.addEventListener('dragover', handleDragOver);
    item.addEventListener('dragend', handleDragEnd);
    item.addEventListener('drop', handleDrop);
  });
