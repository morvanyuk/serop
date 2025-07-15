
document.addEventListener('DOMContentLoaded', function() {
    loadServers();
});

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

document.getElementById('add-server-btn').addEventListener('click', function() {
    let serverName = document.getElementById('new-server-name').value;
    if (serverName) {
        let formData = new FormData();
        formData.append('name', serverName);
        axios.post('/servers/', formData)
            .then(function(response) {
                loadServers();
                document.getElementById('new-server-name').value = '';
            })
            .catch(function(error) {
                alert('Error adding server: ' + error);
            });
    }
});

document.getElementById('add-item-btn').addEventListener('click', function() {
    let itemName = document.getElementById('item-name').value;
    let itemMod = document.getElementById('item-mod').value;
    let itemPrice = document.getElementById('item-price').value;
    let serverId = document.getElementById('server-select').value;

    if (itemName && itemPrice && serverId) {
        let formData = new FormData();
        formData.append('name', itemName);
        formData.append('is_mods', itemMod);
        formData.append('price', itemPrice);
        formData.append('server_id', serverId);
        axios.post('/items/', formData)
            .then(function(response) {
                // Optionally clear fields or give feedback
                document.getElementById('item-name').value = '';
                document.getElementById('item-mod').value = '';
                document.getElementById('item-price').value = '';
                alert('Item added successfully');
            })
            .catch(function(error) {
                alert('Error adding item: ' + error);
            });
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
  let id = event.target.parentNode.dataset.itemId


  let table = document.getElementById('calculator-tbody');
  let node = document.createElement("tr");
  node.dataset.itemId = id;
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
  let serverId = document.getElementById('server-select').value;
  

  axios.get('/search/?field=' + select.value + '&text=' + input.value + '&server_id=' + serverId)
    .then(function (response) {
      let tbody = document.getElementById('search-tbody');
      data = response.data
      tbody.innerHTML = '';
      for (let i = 0; data.length > i; i++){
        let element = JSON.parse(data[i])

        let node = document.createElement("tr");
        node.dataset.itemId = element['id'];

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

document.getElementById('calculate-btn').addEventListener('click', function() {
    let items = [];
    let rows = document.getElementById('calculator-tbody').rows;
    for (let i = 0; i < rows.length; i++) {
        let row = rows[i];
        items.push({
            id: row.dataset.itemId,
            quantity: row.querySelector('input[name="quantity"]').value
        });
    }

    let serverId = document.getElementById('server-select').value;
    let craftType = document.getElementById('simple-calc-checkbox').checked ? 'simple' : 'percentage';

    axios.post('/calculate/', {
        items: items,
        server_id: serverId,
        craft_type: craftType
    })
    .then(function(response) {
        document.getElementById('total-price').innerText = response.data.total_cost;
    })
    .catch(function(error) {
        alert('Error calculating cost: ' + error);
    });
});
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
function loadServers() {
    axios.get('/servers/')
        .then(function(response) {
            let serverSelect = document.getElementById('server-select');
            serverSelect.innerHTML = '';
            response.data.forEach(function(server) {
                let option = document.createElement('option');
                option.value = server.id;
                option.textContent = server.name;
                serverSelect.appendChild(option);
            });
            send_query();
        })
        .catch(function(error) {
            alert('Error loading servers: ' + error);
        });
}