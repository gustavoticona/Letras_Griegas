import tempfile
import os
from flask import Flask, request, redirect, send_file
from skimage import io
import base64
import glob
import numpy as np

app = Flask(__name__)

main_html = """
<html>
<head></head>
<script>
  var mousePressed = false;
  var lastX, lastY;
  var ctx;

   function getRndInteger(min, max) {
    return Math.floor(Math.random() * (max - min) ) + min;
   }

  function InitThis() {
      ctx = document.getElementById('myCanvas').getContext("2d");

      // Por ahora usamos una letra fija
      var letras = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"];

      var randomIndex = Math.floor(Math.random() * letras.length);
      var letraSeleccionada = letras[randomIndex];

      document.getElementById('mensaje').innerHTML = 'Dibuja la letra griega: ' + letraSeleccionada;
      document.getElementById('numero').value = letraSeleccionada;

      $('#myCanvas').mousedown(function (e) {
          mousePressed = true;
          Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, false);
      });

      $('#myCanvas').mousemove(function (e) {
          if (mousePressed) {
              Draw(e.pageX - $(this).offset().left, e.pageY - $(this).offset().top, true);
          }
      });

      $('#myCanvas').mouseup(function (e) {
          mousePressed = false;
      });
  	  $('#myCanvas').mouseleave(function (e) {
          mousePressed = false;
      });
  }

  function Draw(x, y, isDown) {
      if (isDown) {
          ctx.beginPath();
          ctx.strokeStyle = 'black';
          ctx.lineWidth = 11;
          ctx.lineJoin = "round";
          ctx.moveTo(lastX, lastY);
          ctx.lineTo(x, y);
          ctx.closePath();
          ctx.stroke();
      }
      lastX = x; lastY = y;
  }

  function clearArea() {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  function prepareImg() {
    var canvas = document.getElementById('myCanvas');

    // Crear un canvas temporal
    var tempCanvas = document.createElement('canvas');
    var tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;

    // Pintar fondo blanco
    tempCtx.fillStyle = 'white';
    tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

    // Dibujar el contenido del canvas original encima
    tempCtx.drawImage(canvas, 0, 0);

    // Ahora convertir a base64 la imagen con fondo blanco
    document.getElementById('myImage').value = tempCanvas.toDataURL();
}

</script>
<body onload="InitThis();">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>

    <div align="left">
      <img src="https://upload.wikimedia.org/wikipedia/commons/f/f7/Uni-logo_transparente_granate.png" width="300"/>
    </div>


    <div align="center">
        <div>
            <img src="https://www.shutterstock.com/image-vector/greek-alphabet-letters-education-science-600nw-2444755451.jpg" width="400" alt="Guía del alfabeto griego"/>
        </div>
        <h1 id="mensaje">Dibujando una letra griega</h1>
        <canvas id="myCanvas" width="200" height="200" style="border:2px solid black"></canvas>
        <br/><br/>
        <button onclick="javascript:clearArea();return false;">Borrar</button>
    </div>

    <div align="center">
      <form method="post" action="upload" onsubmit="javascript:prepareImg();" enctype="multipart/form-data">
        <input id="numero" name="numero" type="hidden" value="">
        <input id="myImage" name="myImage" type="hidden" value="">
        <input id="bt_upload" type="submit" value="Enviar">
      </form>
    </div>
</body>
</html>
"""

@app.route("/")
def main():
    return(main_html)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        img_data = request.form.get('myImage').replace("data:image/png;base64,","")
        letra = request.form.get('numero')
        print("Letra:", letra)

        if not os.path.exists(letra):
            os.mkdir(letra)

        with tempfile.NamedTemporaryFile(delete=False, mode="w+b", suffix='.png', dir=letra) as fh:
            fh.write(base64.b64decode(img_data))

        print("Imagen guardada")
    except Exception as err:
        print("Error:", err)

    return redirect("/", code=302)

@app.route('/prepare', methods=['GET'])
def prepare_dataset():
    letras = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]
    images = []
    labels = []
    for letra in letras:
        filelist = glob.glob(f'{letra}/*.png')
        imgs = io.concatenate_images(io.imread_collection(filelist))
        imgs = imgs[:, :, :, 3]  # Alpha channel
        images.append(imgs)
        labels.append(np.array([letra] * imgs.shape[0]))
    images = np.vstack(images)
    labels = np.concatenate(labels)
    np.save('X.npy', images)
    np.save('y.npy', labels)
    return "OK!"

@app.route('/X.npy', methods=['GET'])
def download_X():
    return send_file('./X.npy')

@app.route('/y.npy', methods=['GET'])
def download_y():
    return send_file('./y.npy')

if __name__ == "__main__":
    if not os.path.exists('alpha'):
        os.mkdir('alpha')
    app.run()
