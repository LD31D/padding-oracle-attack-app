# Padding Oracle Attack App

This application is intentionally vulnerable and was created for **educational purposes only**, to practice and demonstrate the Padding Oracle Attack against AES-CBC encryption.

## API Endpoints

The server has three endpoints you can hit:

### GET `/get-message`

Gets you a random encrypted message to attack. The server generates some random text, encrypts it with AES-128-CBC and gives you back the ciphertext + IV.

#### Query Params

- `length` - how long you want the plaintext to be (defaults to random 4-15 bytes)

#### Response:

```json
{
  "ciphertext": "2a4b83e4786490f6060f6c3c02554a82",
  "iv": "7f25f06f18cc2eebe7c37578e3a7cf70"
}
```

### POST `/check-padding`

**This is the oracle!** Send it an IV and ciphertext, and it'll tell you if the padding is valid after decryption. This is the vulnerability you exploit.

#### Request body:

```json
{
  "ciphertext": "2a4b83e4786490f6060f6c3c02554a82",
  "iv": "7f25f06f18cc2eebe7c37578e3a7cf70"
}
```

#### Responses:

##### Valid padding:

```json
{
  "ok": true
}
```

##### Invalid padding:

```json
{
  "ok": false,
  "error": "Invalid padding"
}
```

##### Decryption error:

```json
{
  "ok": false,
  "error": "Decryption error"
}
```

### POST `/check-insecure-padding`

Same as `/check-padding`, but uses a custom (insecure) padding check instead of the library function. Good for testing different oracle implementations.

### POST `/check-message`

Decrypts the ciphertext, removes padding, and compares the result with a provided plaintext.

This endpoint can be used to verify a successful attack.

#### Request body:

```json
{
  "ciphertext": "2a4b83e4786490f6060f6c3c02554a82",
  "iv": "7f25f06f18cc2eebe7c37578e3a7cf70",
  "message": "nQEF=e8"
}
```

#### Responses:

##### Message matches:

```json
{
  "ok": true
}
```

##### Message does not match:

```json
{
  "ok": false,
  "error": "Message does not match"
}
```

##### Decryption or padding error:

```json
{
  "ok": false,
  "error": "Decryption or padding error"
}
```

## Running the Application

Clone the repo:

```bash
git clone https://github.com/LD31D/padding-oracle-attack-app.git
cd padding-oracle-attack-app
```

Run with Docker:

```bash
docker build -t padding-oracle .
docker run -p 5834:5834 padding-oracle
```

Server runs on `http://127.0.0.1:5834`

## Typical Attack Flow

1. Call /get-message to obtain (IV, ciphertext)
2. Repeatedly query /check-padding with modified IVs
3. Recover plaintext byte-by-byte
4. Verify result using /check-message
