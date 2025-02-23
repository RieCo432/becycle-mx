import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  writeBikeDetailsToNfcTag(bike) {
    toast.success('Hold To Tag Now', {timeout: 2000});
    return new Promise(async (resolve, reject) => {
      try {
        const encoder = new TextEncoder();
        const ndef = new NDEFReader();
        await ndef.write({
          records: [
            {recordType: 'mime', mediaType: 'application/json', data: encoder.encode(JSON.stringify(bike))},
          ],
        }, {overwrite: true});
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  },
  readBikeDetailsFromNfcTag() {
    return new Promise(async (resolve, reject) => {
      try {
        const ndef = new NDEFReader();
        toast.success('Hold To Tag Now', {timeout: 2000});
        await ndef.scan();

        ndef.addEventListener('readingerror', (error) => {
          reject(error);
        });

        ndef.addEventListener('reading', ({message, serialNumber}) => {
          const record = message.records[0];
          if (record.recordType === 'mime' && record.mediaType === 'application/json') {
            const textDecoder = new TextDecoder();
            const text = textDecoder.decode(record.data);
            const bike = JSON.parse(text);
            resolve(bike);
          }
        });
      } catch (error) {
        reject(error);
      }
    });
  },
};
