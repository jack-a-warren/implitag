/*
 * I (Jack Warren) did not write this code. It was obtained from a tutorial. It
 * has however been slightly modified to work with my application and to
 * function to my liking
 */
function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var ac_list, ac_item, i, full_val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();

      /*do not do autocomplete if search is empty*/
      if (!full_val) { return false;}

      /*do not do autocomplete if search ends with a space or a search operator*/
      if (full_val[full_val.length - 1] == " ") { return false; }
      if (full_val[full_val.length - 1] == "+") { return false; }
      if (full_val[full_val.length - 1] == "-") { return false; }
      if (full_val[full_val.length - 1] == "&") { return false; }
      if (full_val[full_val.length - 1] == "^") { return false; }
      currentFocus = -1;
      var vals = full_val.trim().split(/\s+/);
      var val = vals[vals.length - 1];

      /*create a DIV element that will contain the items (values):*/
      ac_list = document.createElement("DIV");
      ac_list.setAttribute("id", this.id + "autocomplete-list");
      ac_list.setAttribute("class", "autocomplete-list");

      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(ac_list);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        // if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
        if (arr[i].toUpperCase().includes(val.toUpperCase())) {

          /*create a DIV element for each matching element:*/
          ac_item = document.createElement("DIV");
          ac_item.setAttribute("class", "autocomplete-item");

          /*make the matching letters bold:*/
          // ac_item.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          // ac_item.innerHTML += arr[i].substr(val.length);
          ac_item.innerHTML += arr[i]

          /*insert a input field that will hold the current array item's value:*/
          ac_item.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";

          /*execute a function when someone clicks on the item value (DIV element):*/
          ac_item.addEventListener("click", function(e) {
            /*insert the value for the autocomplete text field:*/
            var values_before = full_val.trim().split(/\s+/);
            values_before = values_before.slice(0, values_before.length - 1);

            if (values_before.length == 0) {
              inp.value = this.getElementsByTagName("input")[0].value + " ";
            } else {
              inp.value = values_before.join(" ") + " " + this.getElementsByTagName("input")[0].value + " ";
            }

            /*close the list of autocompleted values,
            (or any other open lists of autocompleted values:*/
            closeAllLists();
          });

          ac_list.appendChild(ac_item);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");

      if (x) x = x.getElementsByTagName("div");
      else return false;

      if (e.keyCode == 40 || e.keyCode == 9) {
        /*If the arrow DOWN  or TAB key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        e.preventDefault();

        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;

        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();

        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;

    /*start by removing the "active" class on all items:*/
    removeActive(x);

    if (currentFocus >= x.length) currentFocus = 0;

    if (currentFocus < 0) currentFocus = (x.length - 1);

    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-list");

    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
      x[i].parentNode.removeChild(x[i]);
    }
  }
}
/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
}
