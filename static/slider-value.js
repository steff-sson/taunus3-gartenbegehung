var slider = document.getElementById("zustand");
var output = document.getElementById("note");
output.innerHTML = slider.value;

slider.oninput = function() {
  output.innerHTML = this.value;
}

// <![CDATA[
  function loading(){
    $("#loading").show();
    $("#content").hide();
        }
// ]]>
