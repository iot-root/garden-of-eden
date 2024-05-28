export const GetImage = async (filename) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/camera/get`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          value: filename,
        }),
      }
    );

    const data = await response.blob();
    const imageUrl = URL.createObjectURL(data);

    if (!response.ok) {
      return data;
    }

    return imageUrl;
  } catch (e) {
    console.error('Error fetching images: ', e);
    throw e;
  }
};

export const CaptureImages = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/camera/capture`
    );

    const data = await response.json();

    if (!response.ok) {
      return data;
    }

    return data;
  } catch (e) {
    console.error('Error capturing images: ', e);
    throw e;
  }
};

export const ListImages = async () => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/camera/list-images`
    );

    const data = await response.json();

    if (!response.ok) {
      return data;
    }

    return data;
  } catch (e) {
    console.error('Error fetching images list: ', e);
    throw e;
  }
};

export const DeleteImage = async (filename) => {
  try {
    const response = await fetch(
      `http://${import.meta.env.VITE_PI_IP}:${import.meta.env.VITE_API_PORT}/camera/delete`,
      {
        method: 'POST',
        body: JSON.stringify({
          value: filename,
        }),
        headers: { 'Content-Type': 'application/json' },
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return data;
    }

    return data;
  } catch (e) {
    console.error('Error deleting image: ', e);
    throw e;
  }
};
