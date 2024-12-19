function add_car(){
    var brand = document.getElementById('brand').value;
    var model = document.getElementById('model').value;
    var price = document.getElementById('price').value;

    if (!brand || !model || !price) {
                alert('All fields are required!');
                return;
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            var json = JSON.parse(this.responseText);
            alert(json.message);

            document.getElementById('brand').value = "";
            document.getElementById('model').value = "";
            document.getElementById('price').value = "";
        }
    };

    xhttp.open('POST', '/add_car', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');

    xhttp.send(JSON.stringify({
        brand: brand,
        model: model,
        price: price
    }));
}