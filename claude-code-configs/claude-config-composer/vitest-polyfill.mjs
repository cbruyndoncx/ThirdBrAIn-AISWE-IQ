// Polyfill for crypto.getRandomValues for Node < 19
import crypto from 'crypto';

if (!globalThis.crypto) {
  globalThis.crypto = crypto;
}
if (!globalThis.crypto.getRandomValues) {
  globalThis.crypto.getRandomValues = function(array) {
    return crypto.randomFillSync(array);
  };
}
