/* Project specific Javascript goes here. */


var N = 1024, r = 8, p = 1;

var dkLen = 32;

function gen_key(password, salt) {
    password_buffer = new buffer.SlowBuffer(password.normalize("NFKC"));
    salt_buffer = new buffer.SlowBuffer(salt.normalize("NFKC"));
    scrypt(password_buffer, salt_buffer, N, r, p, dkLen, function(error, progress, key) {
            if (error) {
              console.log("Error: " + error);

            } else if (key) {
              console.log("Found: " + key);

            } else {
              // update UI with progress complete
              console.log(progress);
            }
          });
}
