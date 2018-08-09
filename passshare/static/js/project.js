/* Project specific Javascript goes here. */


var N = 1024, r = 8, p = 1;

var dkLen = 32;

function encrypt_data(num_words, data, attempts) {
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
    try{
        scrypt(password_buffer, salt_buffer, N, r, p, dkLen, function(error, progress, key) {
            if (error) {
                key_fail_callback(num_words, data, attempts);

            } else if (key) {
                console.log("Found: " + key);
                var text_bytes = aesjs.utils.utf8.toBytes(data);
                var aes_ctr = new aesjs.ModeOfOperation.ctr(key);
                var encrypted_bytes = aes_ctr.encrypt(text_bytes);
                //var encrypted_hex = aesjs.utils.hex.fromBytes(encrypted_bytes);

                console.log(btoa(encrypted_bytes));
            } else {
                // update UI with progress complete
                console.log(progress);
            }
        });
    } catch(err) {
        key_fail_callback(num_words, data, attempts);
    }
}

function key_fail_callback(num_words, data, attempts){
    encrypt_data(num_words, data, attempts - 1);
}

function get_random_word(){
    var array = new Uint32Array(1);
    window.crypto.getRandomValues(array);
    var item = word_list[array[0] % word_list.length];
    return item;
}
