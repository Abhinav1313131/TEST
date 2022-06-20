async function load() {
    let url = 'https://dry-cove-78274.herokuapp.com/';
    let myJson = await (await fetch(url)).json();
    console.log(myJson);
    var dname = myJson.map(function (obj) {
        return obj.domainName;
    });
    console.log(dname);
    var hcode = myJson.map(function (obj) {
        return obj.hexCode;
    });
    console.log(hcode);
    
    for(const headerName of dname){
    const div1 = document.createElement("div");
    div1.className = 'card';
    div1.id = 'cards';
    document.getElementById("rows").appendChild(div1);
    }

const parentObject = document.getElementsByClassName('card');

[...parentObject].forEach((parent, i) => {
    const childElement = document.createElement('div');
    childElement.className = 'container'; 
    parent.appendChild(childElement)
});

const parentObject1 = document.getElementsByClassName('container');

[...parentObject1].forEach((parent1, i) => {
    const childElement1 = document.createElement('h4');
    childElement1.id = 'domain';
    parent1.appendChild(childElement1)
});

for(const headerName1 of dname) {
    const headerNumber = dname.indexOf(headerName1);
    const header = document.querySelectorAll('h4')[headerNumber];
    header.textContent = headerName1;
    }

    
}

load();