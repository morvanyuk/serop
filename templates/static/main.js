let parentItems = []
let craftItem;

document.getElementById('link').href = `/crud/${window.location.pathname.split('/')[2]}`
document.getElementById('link').innerText = "Список"

send_query()
document.querySelector('#search-input').addEventListener('input', function(event) {
  send_query()
});

document.querySelector('.custom-checkbox-wrapper').addEventListener('input', function(event) {
  if (document.getElementById('customCheckbox1').checked){
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) * 1.05
  } else {
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) / 1.05 
  }
});

function add_to_total_price(price){
  if (document.getElementById('customCheckbox1').checked){
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) + parseFloat(price)  * 1.05
  } else {
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) + parseFloat(price)
  }
}

function remove_from_total_price(price){
  if (document.getElementById('customCheckbox1').checked){
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) - parseFloat(price)  * 1.05
  } else {
    document.getElementById('total-price').innerText = parseFloat(document.getElementById('total-price').innerText) - parseFloat(price)
  }
}

function add_to_calc(event) {
  let id = event.target.parentNode.querySelector('.id').innerText
  let name = event.target.parentNode.querySelector('.name').innerText
  let mod = event.target.parentNode.querySelector('.mode').innerText
  let price = event.target.parentNode.querySelector('p').innerText

  let craft_element = document.getElementById('craft-element-tbody');
  let table = document.getElementById('calculator-tbody');
  // Додати предмет на головну
  if (craft_element.childNodes.length == 0){
    craftItem = id
    craft_element.innerHTML = `<p id='main-id'>${id}</p>
              <td class='key'>${id.split("/")[1]}</td>
              <td>${name}</td>
              <td>${mod}</td>
              <td>${price}</td>
              <td><button onclick="remove_from_craft_spaace()" type="button" class="btn btn-outline-danger">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16">
                <path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5M11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47M8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5"></path></svg>
                Видалити
              </button></td>`
  } else {
    // if (craftItems.includes(id)) {
      // return alert("")
    // }
    if (id == craftItem){
      return alert('Предмет не можна крафтити з нього')
    }
    let node = document.createElement("tr");
    node.innerHTML = `<p id='item-id'>${id}</p>
              <td class='id'>${id.split("/")[1]}</td>
              <td>${name}</td>
              <td>${mod}</td>
              <td class='price'>${price}</td>
              <td><div id="counter">
                <span type="button" onclick="minus(event) "id="minus" class="btn btn-secondary">-</span>
                <input type="number" step="1" min="0" value="1" name="quantity">
                <span type="button" onclick="plus(event)" id="plus" class="btn btn-secondary">+</span>
            </div></td>`
    table.insertBefore(node, table.firstChild);
    if (!parentItems.some(item => Object.keys(item)[0] == id)) {
      parentItems.push({ [id]: 1 });
    } else {
      const item = parentItems.find(obj => Object.keys(obj)[0] == id);

      if (item) {
          item[id] = item[id] + 1;
      }
    }

    add_to_total_price(price)
  }
}
function send_query() {
  let input = document.getElementById('search-input')
  let select = document.getElementById('search-select')

  axios.get('/search/?field=' + select.value + '&text=' + input.value + '&graph_name=' + window.location.pathname.split('/')[2])
    .then(function (response) {
      let tbody = document.getElementById('search-tbody');
      data = response.data
      tbody.innerHTML = '';
      for (let i = 0; data.length > i; i++){
        let node = document.createElement("tr");
        node.innerHTML = `<td onclick='add_to_calc(event)' 
        class="name">${data[i]['name']}</td><td onclick='add_to_calc(event)'
         class="mode">${data[i]['mod']}</td><p class="price">${data[i]['price']}</p><p class="id">${data[i]['id']}</p>`;
        tbody.appendChild(node);
      }
      
      
    })
    .catch(function (error) {
      // handle error
      console.log(error);
    })
}
function plus(event){
  let price = event.target.parentNode.parentNode.parentNode.querySelector('.price').innerText
  let id = event.target.parentNode.parentNode.parentNode.querySelector('#item-id').innerText
  const item = parentItems.find(obj => Object.keys(obj)[0] == id);

    if (item) {
        item[id] = item[id] + 1;
    }
  add_to_total_price(price)
  event.target.parentNode.querySelector('input').value = parseFloat(event.target.parentNode.querySelector('input').value) + 1
}
function minus(event){
  let price = event.target.parentNode.parentNode.parentNode.querySelector('.price').innerText
  let id = event.target.parentNode.parentNode.parentNode.querySelector('#item-id').innerText
  let new_value = parseFloat(event.target.parentNode.querySelector('input').value) - 1

  const itemIndex = parentItems.findIndex(obj => Object.keys(obj)[0] == id);

  if (itemIndex !== -1) {
    const item = parentItems[itemIndex];
    item[id] = item[id] - 1;

    if (item[id] === 0) {
        parentItems.splice(itemIndex, 1); // Видаляємо об'єкт з масиву
    }
  }

  remove_from_total_price(price)

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
  let craft_element = document.getElementById("main-id").innerText
  let check = false;
  if (document.getElementById('customCheckbox1').checked){
    check = true
  }

  const parents = parentItems.reduce((acc, obj) => ({...acc, ...obj}), {});
  axios.post('/craft/', { key: craft_element, parents: 
    parents, plus5: check, graph:  pathArray = window.location.pathname.split('/')[2]})
    .then((response) => {
      location.reload();
    })
    .catch(function (error) {
      // handle error
      console.log(error);
    })
}