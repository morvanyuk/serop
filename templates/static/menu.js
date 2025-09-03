function render(){
  axios.get('/get-all-graphs')
    .then(function (response) {
    let tbody = document.getElementById('tbody');
    data = response.data
    for (let i = 0; data.length > i; i++){

      let node = document.createElement("tr");

      node.innerHTML = `<td scope="row">${i + 1}</td>
      <td><a href="/crud/${data[i]}">${data[i]}</a></td>`;
      tbody.appendChild(node);
    }
    
    
  })
  .catch(function (error) {
    // handle error
    alert(error);
  })
}

function create_graph(event) {
  event.preventDefault();
  const data = document.getElementById("itemName").value;
  
  axios.post('/create-graph/', { name: data })
    .then(response => {
      location.reload();
    })
    .catch(error => {
      console.log(error)
    });
}

render()