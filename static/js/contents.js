'use strict';

class ProductCart {
    #ENDPOINT = '/api/product-cart';
    #UPDATE_ENDPOINT = '/api/update-product-cart';

    constructor() {
        let self = this;
        fetch(self.#ENDPOINT).then(function (response) {
            return response.json().then(function (json) {
                self.render(json);
            });
        });
    }

    render(data) {
        let items = '';
        let total = 0;
        for (let product of data) {
            const user = product['user'];
            const name = product['name'];
            const description = product['description'];
            const count = product['count'];
            const price = product['price'];
            const photo1 = product['photo1'];
            const product_id = product['product_id'];
            const mediaType = product['media_type']
            const data_price = price * count
            let mediaContent;
            total += price * count;

            if(mediaType === 'image'){
                mediaContent = `<img src="${photo1}" class="product-image" alt="image">`
            } else if (mediaType === 'video'){
                mediaContent = `<video class="product-image" autoplay loop muted playsinline><source src="${photo1}" type="video/mp4"></video>`
            } else {
                mediaContent = `<p class="product-image">Unsupported media type</p>`
            }

            let content = `<div class="product-block" id="product-${product_id}">
                ${mediaContent}
                <p class="product-name">${name}</p>
                <p class="product-price">${price}$</p>
                <div class="quantity-control">
                    <input type="number" class="quantity-input" value="${count}" min="1" max="100" 
                    data-product-id="${product_id}" data-product-price="${price}">
                    <button id="del-btn-cart" class="delete-btn" data-product-id="${product_id}" data-product-price="${data_price}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
                <p class="error-message" style="color: red; display: none;">Invalid value</p>
            </div>`;
            items += content;
        }

        document.querySelector('#product-box').innerHTML = `<div id="product-items">${items}</div>`;
        if (total === 0) {
            document.getElementById('buy-cart').classList.add('hidden');
        } else {
            document.getElementById('buy-cart').classList.remove('hidden');
        }
        document.getElementById('subtotal').textContent = `Subtotal ${total} $`;

        // EventListener cart change
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', (event) => {
                this.updateSubtotal(event);
            });
        });
    }

    updateSubtotal(event) {
        const input = event.target;
        const productId = input.getAttribute('data-product-id');
        const newCount = parseInt(input.value);

        if (isNaN(newCount) || newCount < 1 || newCount > 100) {
            const errorMessage = input.closest('.product-block').querySelector('.error-message');
            errorMessage.style.display = 'block';
            return;
        } else {
            const errorMessage = input.closest('.product-block').querySelector('.error-message');
            errorMessage.style.display = 'none';
        }

        let total = 0;
        document.querySelectorAll('.quantity-input').forEach(input => {
            const count = parseInt(input.value);
            const price = parseFloat(input.getAttribute('data-product-price'));
            total += count * price;

            const deleteButton = document.querySelector(
                `.delete-btn[data-product-id='${input.getAttribute('data-product-id')}']`);
            if (deleteButton) {
                deleteButton.setAttribute('data-product-price', (count * price));
            }
        });

        document.getElementById('subtotal').textContent = `Subtotal ${total} $`;


        fetch(this.#UPDATE_ENDPOINT, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({product_id: productId, count: newCount})
        }).then(response => response.json())
            .then(json => {
                if (!json.success) {
                    console.log('Error update')
                }
            })

    }
}

