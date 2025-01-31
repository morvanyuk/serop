
send_query()
document.querySelector('#search-input').addEventListener('input', function(event) {
  send_query()
});
document.querySelector('#simple-calc').addEventListener('click', function(event) {
  if (document.getElementById('calc-plus-5-checkbox').checked){
    document.getElementById('simple-calc').style.borderBottom = "2px solid aqua";
    document.getElementById('calc-plus-5').style.borderBottom = "none";
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) / 1.05
    document.getElementById('calc-plus-5-checkbox').checked = false
    document.getElementById('simple-calc-checkbox').checked = true
  }
});
document.querySelector('#calc-plus-5').addEventListener('click', function(event) {
  if (document.getElementById('simple-calc-checkbox').checked){
    document.getElementById('calc-plus-5').style.borderBottom = "2px solid aqua";
    document.getElementById('simple-calc').style.borderBottom = "none";
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) * 1.05
    document.getElementById('calc-plus-5-checkbox').checked = true
    document.getElementById('simple-calc-checkbox').checked = false
  }
});

function add_to_total_price(price){
  if (document.getElementById('simple-calc-checkbox').checked){
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) + parseFloat(price)
  } else {
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) + parseFloat(price) * 1.05
  }
}

function add_to_calc(event) {
  let name = event.target.parentNode.querySelector('.name').innerText
  let mod = event.target.parentNode.querySelector('.mode').innerText
  let price = event.target.parentNode.querySelector('p').innerText


  let table = document.getElementById('calculator-tbody');
  let node = document.createElement("tr");
  node.innerHTML = `<td>${name}</td>
            <td>${mod}</td>
            <td class='price'>${price}</td>
            <td><div id="counter">
              <span type="button" onclick="minus(event) "id="minus" class="btn btn-secondary">-</span>
              <input type="number" step="1" min="0" value="1" name="quantity">
              <span type="button" onclick="plus(event)" id="plus" class="btn btn-secondary">+</span>
           </div></td>`
  table.insertBefore(node, table.firstChild);
  add_to_total_price(price)

}
function send_query() {
  let input = document.getElementById('search-input')
  let select = document.getElementById('search-select')
  

  axios.get('/search/?field=' + select.value + '&text=' + input.value)
    .then(function (response) {
      let tbody = document.getElementById('search-tbody');
      data = response.data
      tbody.innerHTML = '';
      for (let i = 0; data.length > i; i++){
        let element = JSON.parse(data[i])

        let node = document.createElement("tr");

        node.innerHTML = `<td onclick='add_to_calc(event)' 
        class="name">${element['name']}</td><td onclick='add_to_calc(event)' class="mode">${element['mod']}</td><p>${element['price']}</p>`;
        tbody.appendChild(node);
      }
      
      
    })
    .catch(function (error) {
      // handle error
      alert(error);
    })
}
function plus(event){
  let price = event.target.parentNode.parentNode.parentNode.querySelector('.price').innerText
  add_to_total_price(price)
  event.target.parentNode.querySelector('input').value = parseFloat(event.target.parentNode.querySelector('input').value) + 1
}
function minus(event){
  let price = event.target.parentNode.parentNode.parentNode.querySelector('.price').innerText
  let new_value = parseFloat(event.target.parentNode.querySelector('input').value) - 1

  if (document.getElementById('simple-calc-checkbox').checked){
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) - parseFloat(price)
  } else {
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) - parseFloat(price) * 1.05
  }
  if (new_value == 0){
    event.target.parentNode.parentNode.parentNode.remove();
    let elements = document.getElementById('calculator-tbody').childElementCount;
    if (elements == 0){
      document.getElementById('total-price').innerText = 0;
    }
  } else {
    event.target.parentNode.querySelector('input').value = new_value;
    
  }
  
}