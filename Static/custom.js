// Handling multiple modals
let modals = document.getElementsByClassName('modal');
let modalBtns = document.getElementsByClassName('modal-btn');
let closeBtns = document.getElementsByClassName('close');

for(let modalBtn of modalBtns) {
  let target = document.getElementById(modalBtn.getAttribute('target'));
  modalBtn.onclick = function() {  
      target.style.display = 'block';
  }
}

for(let closeBtn of closeBtns) {
  let toClose =  closeBtn.parentNode.parentNode.parentNode.parentNode;
  closeBtn.onclick = function() {
      toClose.style.display = 'none';
  }
}

window.onkeydown = function(event) {
  if (event.key == 'Escape') {
      for(let modal of modals) {
          modal.style.display = 'none';
      }
  }
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  for(let modal of modals) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  }
}