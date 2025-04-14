
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
  let id = event.target.parentNode.querySelector('.id').innerText
  let name = event.target.parentNode.querySelector('.name').innerText
  let mod = event.target.parentNode.querySelector('.mode').innerText
  let price = event.target.parentNode.querySelector('p').innerText

  let craft_element = document.getElementById('craft-element-tbody');
  let table = document.getElementById('calculator-tbody');
  if (craft_element.childNodes.length == 0){
    craft_element.innerHTML = `<td class='id'>${id}</td>
              <td>${name}</td>
              <td>${mod}</td>
              <td>${price}</td>
              <td><button onclick="remove_from_craft_spaace()" type="button" class="btn btn-outline-danger">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
                <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5M11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47M8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5"></path></svg>
                Видалити
              </button></td>`
  } else {
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
        class="name">${element['name']}</td><td onclick='add_to_calc(event)'
         class="mode">${element['mod']}</td><p class="price">${element['price']}</p><p class="id">${element['id']}</p>`;
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
function remove_from_craft_spaace(){
  let craft_element = document.getElementById('craft-element-tbody');
  craft_element.innerHTML = "";
}
function craft(){
  let craft_element = document.getElementById('craft-element-tbody')
  let id = parseInt(craft_element.querySelector('.id').innerText)
  let price = parseFloat(document.getElementById('total-price').innerText);
  let data = { id_element: id, price:  price};
  axios.post('/update', data)
    .then((response) => {
      location.reload();
    })
    .catch(function (error) {
      // handle error
      alert(error);
    })
}