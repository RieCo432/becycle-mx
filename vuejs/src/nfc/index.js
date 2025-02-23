import {useToast} from 'vue-toastification';

const toast = useToast();

export default {
  writeBikeDetailsToNfcTag(bike) {
    toast.success('Hold To Tag Now', {timeout: 2000});
    return new Promise(async (resolve, reject) => {
      try {
        const encoder = new TextEncoder();
        const jsonString = JSON.stringify(bike);
        const encodedJsonString = encoder.encode(jsonString);
        const ndef = new NDEFReader();
        await ndef.write({
          records: [
            {recordType: 'mime', mediaType: 'application/json', data: encodedJsonString},
          ],
        }, {overwrite: true});

        const abortController = new AbortController();

        await ndef.scan({signal: abortController.signal});

        const event = await new Promise((resolve) => {
          ndef.onreading = (event) => resolve(event);
        });

        const record = event.message.records[0];

        if (record.recordType === 'mime' && record.mediaType === 'application/json') {
          const textDecoder = new TextDecoder();
          const text = textDecoder.decode(record.data);
          if (text && (text === jsonString)) {
            resolve(event.serialNumber);
          } else {
            reject(new Error('Correctness of written tag could not be verified.'));
          }
        } else {
          reject(new Error('Something went wrong'));
        }

        await new Promise((r) => setTimeout(r, 3000));
        abortController.abort();
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
          console.log(serialNumber);
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
