Probar primero en el ambiente de produccion

Para hacer las pruebas unitarias hay que cambiar entre distintos entornos
$env:DJANGO_ENV="test"  -Nos permite entrar en el entorno de test, no es necesario hacer migraciones ya que implemente en el settings que se hagan apenas se runee

y para Volver al entorno de desarrollo es $env:DJANGO_ENV="production"

