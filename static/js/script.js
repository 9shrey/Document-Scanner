function uploadImage() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  if (!file) {
      alert("Please choose a file first.");
      return;
  }
  const formData = new FormData();
  formData.append("image", file);

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Upload success:", data);
      document.getElementById("output").innerHTML = `
        <p>Document uploaded successfully.</p>
        <img src="/static/processed_image.jpg" alt="Processed Image">`;
    })
    .catch((error) => {
      console.error("Error uploading image:", error);
    });
}
