/* Project specific Javascript goes here. */


var N = 1024, r = 8, p = 1;

var dkLen = 32;

function encrypt_data(num_words, data, attempts, modal_body_elem) {
    if(attempts <= 0){
        console.log("Out of attempts. Giving up.");
        return;
    }

    var word_array = [];
    for(var i = 0; i < num_words; i++){
        word_array.push(get_random_word());
    }
    var passphrase = word_array.join(" ");

    password_buffer = new buffer.SlowBuffer(passphrase.normalize("NFKC"));
    salt_buffer = new buffer.SlowBuffer(username.normalize("NFKC"));

    password_array = [...password_buffer];
    try{
        scrypt(password_array, salt_buffer, N, r, p, dkLen, function(error, progress, key) {
            if (error) {
                key_fail_callback(num_words, data, attempts, modal_body_elem);

            } else if (key) {
                console.log("Found: " + key);
                var text_bytes = aesjs.utils.utf8.toBytes(data);
                var aes_ctr = new aesjs.ModeOfOperation.ctr(key);
                var encrypted_bytes = aes_ctr.encrypt(text_bytes);
                //var encrypted_hex = aesjs.utils.hex.fromBytes(encrypted_bytes);

                var encrypted_base64 = btoa(encrypted_bytes);
                console.log(encrypted_base64);

                update_modal(word_array, encrypted_base64, modal_body_elem);
            } else {
                // update UI with progress complete
                console.log(progress);
            }
        });
    } catch(err) {
        key_fail_callback(num_words, data, attempts, modal_body_elem);
    }
}

function key_fail_callback(num_words, data, attempts, modal_body_elem){
    encrypt_data(num_words, data, attempts - 1, modal_body_elem);
}

function get_random_word(){
    var array = new Uint32Array(1);
    window.crypto.getRandomValues(array);
    var item = word_list[array[0] % word_list.length];
    return item;
}

function update_modal(words, encrypted_str, modal_body_elem){
    var display_encrypted_str = "";
    if(encrypted_str.length > 32){
        display_encrypted_str = encrypted_str.slice(0, 32) + '...';
    } else {
        display_encrypted_str = encrypted_str;
    }

    var html_str = "";
    html_str += '<div class="card">';
    html_str += '<div class="card-header">';
    html_str += '<h5 class="card-title">Encryption Words</h5>';
    html_str += '</div>';
    html_str += '<ul class="list-group list-group-flush">';

    for(var i = 0; i < words.length; i++){
        html_str += '<li class="list-group-item">' + words[i] + '</li>';
    }

    html_str += '</ul>';
    html_str += '<div class="card-header">';
    html_str += '<h5 class="card-title">Encrypted Data</h5>';
    html_str += '</div>';
    html_str += '<div class="card-body">';
    html_str += '<div class="row">' + display_encrypted_str + '</div>';
    html_str += '</div>';
    html_str += '</div>'; // card

    modal_body_elem.innerHTML = html_str;
}
