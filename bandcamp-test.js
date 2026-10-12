
import bcfetch from 'bandcamp-fetch';

async function testBandcamp() {
  try {
    console.log('Testing Bandcamp discovery...');

    const options = await bcfetch.discovery.getAvailableOptions();

    console.log(JSON.stringify(options, null, 2));
  } catch (error) {
    console.error('Bandcamp test failed:', error);
    process.exitCode = 1;
  }
}

testBandcamp();
