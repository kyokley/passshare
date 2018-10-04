var N = 1024, r = 8, p = 1;

var dkLen = 32;

var encryption_words;
var encrypted_str;
var share_label;
var release_countdown;
var unencrypted_hash;

function create_text_share(num_words, data, countdown, label, modal_elem){
    encryption_words = "";
    encrypted_str = "";
    release_countdown = countdown;
    share_label = label;
    unencrypted_hash = "";

    encrypt_data(num_words, data, 1000, modal_elem);
}

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
    //data_buffer = new buffer.SlowBuffer(data.normalize("NFKC"));

    var raw_data_hash = sha256.create();
    raw_data_hash.update((username + data).normalize("NFKC"));
    unencrypted_hash = raw_data_hash.hex();

    password_array = [...password_buffer];
    //data_array = [...data_buffer];
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

                encryption_words = word_array;
                encrypted_str = encrypted_base64;
                update_modal(modal_body_elem);
            } else {
                // update UI with progress complete
                console.log(progress);
            }
        });

        //scrypt(data_array, salt_buffer, N, r, p, dkLen, function(error, progress, key) {
        //    if (key) {
        //        console.log("Hash key: " + key);
        //        unencrypted_hash = btoa(key);
        //    }
        //});
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

function display_full_data_in_new_window(data){
    var new_window = window.open("", "_blank");
    if(data.length > 80){
        var split_str = "";
        var i = 0;
        while((i + 1) * 80 < data.length){
            split_str += data.slice(i * 80, (i + 1) * 80) + "<br />";
            i++;
        }
        split_str += data.slice(i * 80, data.length);

        new_window.document.write(split_str);
    } else {
        new_window.document.write(data);
    }
}

function update_modal(modal_body_elem){
    var display_encrypted_str = "";
    if(encrypted_str.length > 32){
        display_encrypted_str += '<button class="btn btn-link" onclick="display_full_data_in_new_window(\'' + encrypted_str + '\')">';
        display_encrypted_str += encrypted_str.slice(0, 32) + '...';
        display_encrypted_str += '</button>'
    } else {
        display_encrypted_str = encrypted_str;
    }

    var html_str = "";
    html_str += '<div class="card">';
    html_str += '<div class="card-header">';
    html_str += '<h3 class="card-title">Encrypted Data</h3>';
    html_str += '</div>';
    html_str += '<div class="card-body">';
    html_str += display_encrypted_str;
    html_str += '</div>';
    html_str += '<div class="card-header">';
    html_str += '<h3 class="card-title">Encryption Words</h5>';
    html_str += '</div>';
    html_str += '<ul class="list-group list-group-flush">';

    for(var i = 0; i < encryption_words.length; i++){
        html_str += '<li class="list-group-item">' + encryption_words[i] + '</li>';
    }

    html_str += '</ul>';
    html_str += '</div>'; // card
    html_str += '<div class="card">';
    html_str += '<div class="card-header">';
    html_str += '<h3 class="card-title">Countdown</h3>';
    html_str += '</div>';
    html_str += '<div class="card-body">';
    html_str += release_countdown;
    html_str += '</div>';
    html_str += '</div>';
    html_str += '<div class="card">';
    html_str += '<div class="card-header">';
    html_str += '<h3 class="card-title">Warning</h5>';
    html_str += '</div>';
    html_str += '<div class="card-body">';
    html_str += '<h5>';
    html_str += '<p>By clicking upload below, your encrypted data will be uploaded to the server. The words used for encryption will <strong>NOT</strong> be transmitted in any way.</p>';
    html_str += '<p>Be sure to write your encryption words down or store them someplace secure.</p>';
    html_str += '<p></p>';
    html_str += '<p><strong>** If those words are lost there is no way to recover your data. **</strong></p>';
    html_str += '</h5>';
    html_str += '</div>';
    html_str += '</div>';
    html_str += '</div>'; // card

    modal_body_elem.innerHTML = html_str;
}

function recover_modal(modal_body_elem){
    var display_encrypted_str = "";
    if(encrypted_str.length > 32){
        display_encrypted_str += '<button class="btn btn-link" onclick="display_full_data_in_new_window(\'' + encrypted_str + '\')">';
        display_encrypted_str += encrypted_str.slice(0, 32) + '...';
        display_encrypted_str += '</button>'
    } else {
        display_encrypted_str = encrypted_str;
    }

    var html_str = "";
    html_str += '<div class="card">';
    html_str += '    <div class="card-header">';
    html_str += '        <h3 class="card-title">Request Secret Access</h3>';
    html_str += '    </div>';
    html_str += '    <div class="card-body">';
    html_str += display_encrypted_str;
    html_str += '    </div>';
    html_str += '    <div class="card-header">';
    html_str += '    </div>';
    html_str += '</div>';

    modal_body_elem.innerHTML = html_str;

}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function upload_data(){
    var csrftoken = getCookie('csrftoken');

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload(true);
        }
    };
    xhttp.open("POST", "/secret/api/text_secret/", true);

    var data = {"countdown": release_countdown,
                "unencrypted_hash": unencrypted_hash,
                "label": share_label,
                "data": encrypted_str}

    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send(JSON.stringify(data));
}

function delete_share(pk){
    var csrftoken = getCookie('csrftoken');

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        console.log("Statuscode: " + this.status);
        if (this.readyState == 4 && (this.status == 200 || this.status == 204)) {
            location.reload(true);
        }
    };
    xhttp.open("DELETE", "/secret/api/text_secret/" + pk + "/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrftoken);
    xhttp.send();
}
