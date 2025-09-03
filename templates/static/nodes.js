  
  const modal = new bootstrap.Modal(document.getElementById('itemModal'));

  const form = document.getElementById('itemForm');
  const tableBody = document.getElementById('itemsTableBody');
  const modalTitle = document.getElementById('itemModalLabel');

  const itemIdInput = document.getElementById("itemId");
  const itemPriceInput = document.getElementById("itemPrice");
  const itemNameInput = document.getElementById("itemName");
  const itemModInput = document.getElementById("itemMod");
  document.getElementById("graph").value = window.location.pathname.split('/')[2];

  document.querySelector('#search-input').addEventListener('input', function(event) {
    send_query()
  });
  
  document.getElementById('link').href = `/craft/${window.location.pathname.split('/')[2]}`
  document.getElementById('link').innerText = "Крафт"

  // API: отримати всі предмети
  function fetchItems() {
    pathArray = window.location.pathname.split('/');
    return axios.get('/nodes/' + pathArray[2]);
  }

  function send_query() {
    pathArray = window.location.pathname.split('/');
    let input = document.getElementById('search-input')
    let select = document.getElementById('search-select')
  
    axios.get('/search/?field=' + select.value + '&text=' + input.value + "&graph_name=" + pathArray[2])
      .then(function (response) {
        tableBody.innerHTML = '';
      response.data.forEach(item => {
        const row = `
          <tr id="${item.id}">
            <td>${item.id}</td>
            <td class="item-name">${item.name}</td>
            <td class="item-mod">${item.mod}</td>
            <td class="item-price">${item.price.toFixed(2)}</td>
            <td class="item-elementar">${item.is_elementar}</td>
            <td>
              <button class="btn btn-sm btn-warning me-2" onclick="openEditModal('${item.id}')">Редагувати</button>
              <button class="btn btn-sm btn-danger" onclick="deleteItem('${item.id}')">Видалити</button>
            </td>
          </tr>
        `;
        tableBody.innerHTML += row;
      });
    });
    
  }


  // API: додати новий предмет
  function addItem(data) {
    const newItem = {
      id: Date.now(),
      name: data.name,
      price: parseFloat(data.price)
    };
    items.push(newItem);
    return Promise.resolve(newItem);
  }

  // API: оновити предмет
  function updateItem(id, data) {
    const index = items.findIndex(item => item.id === id);
    if (index !== -1) {
      items[index].name = data.name;
      items[index].price = parseFloat(data.price);
    }
    return Promise.resolve(items[index]);
  }

  // Відображення таблиці
  function renderTable() {
    fetchItems().then(data => {
      tableBody.innerHTML = '';
      data.data.forEach(item => {
        const row = `
          <tr id="${item.id}">
            <td>${item.id}</td>
            <td class="item-name">${item.name}</td>
            <td class="item-mod">${item.mod}</td>
            <td class="item-price">${item.price.toFixed(2)}</td>
            <td class="item-elementar">${item.is_elementar}</td>
            <td>
              <button class="btn btn-sm btn-warning me-2" onclick="openEditModal('${item.id}')">Редагувати</button>
              <button class="btn btn-sm btn-danger" onclick="deleteItem('${item.id}')">Видалити</button>
            </td>
          </tr>
        `;
        tableBody.innerHTML += row;
      });
    });
  }


  // Відкриття модального вікна для створення
  function openCreateModal() {
    modalTitle.textContent = "Додати предмет";
    itemIdInput.value = '';
    itemNameInput.value = '';
    itemPriceInput.value = '';
    itemModInput.value = '';
  }

  // Відкриття модального вікна для редагування
  function openEditModal(id) {
      const node = document.getElementById(id)
      modalTitle.textContent = "Редагувати предмет";
      itemIdInput.value = id;
      itemNameInput.value = node.querySelector(".item-name").innerText;
      itemPriceInput.value = node.querySelector(".item-price").innerText;
      itemModInput.value = node.querySelector(".item-mod").innerText;
      if (node.querySelector(".item-elementar").innerText == 'Ні'){
        document.getElementById("itemPrice").setAttribute("readonly", true);
      } else {
        document.getElementById("itemPrice").readOnly = false;
      }
      modal.show();
  }

  // Надсилання форми
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    if (!itemIdInput.value){

      axios.post('/nodes/create/', {
        name: itemNameInput.value,
        mod: itemModInput.value,
        price: itemPriceInput.value,
        graph: window.location.pathname.split('/')[2]
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        location.reload();
      })
      .catch(error => {
        alert(error.detail);
      });
    } else {
      axios.post('/nodes/update/', {
        id_element: itemIdInput.value,
        name: itemNameInput.value,
        mod: itemModInput.value,
        price: itemPriceInput.value,
        graph: window.location.pathname.split('/')[2]
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        location.reload();
      })
      .catch(error => {
        alert(error.detail);;
      });
    }
    
  }
    
  );
  function deleteItem(id) {
    if (confirm(`Ви справді хочете видалити ${id}`) == true) {
      axios.post('/nodes/delete/', {
        id_element: id,
        graph: window.location.pathname.split('/')[2]
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        renderTable();
      })
      .catch(error => {
        alert(error.response.data.detail);
      });
    }
    
  }
  renderTable(); // Перший рендер

