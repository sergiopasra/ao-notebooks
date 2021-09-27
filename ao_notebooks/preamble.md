---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Uso de python


Los problemas presentados a continuación están resueltos utilizando Python
con la ayuda de una serie de paquetes adicionales, como `numpy` o `matplotlib`.

En particular se utiliza `astropy` para facilitar el manejo de ángulos
en grados y la conversión de unidades.


Para manejar ángulos y unidades, necesitamos la clase `Angle`, así como 
el módulo especial `astropy.units`.

```{code-cell} ipython3
from astropy.coordinates import Angle
import astropy.units as u
```

Con este módulo, ya podemos manejar ángulos de manera natural. Por ejemplo,
creando un objeto con grados minutos y segundos:

```{code-cell} ipython3
Angle("45d34m12.3s")
```

```{code-cell} ipython3
Angle((45, 34, 12.23), unit='degree')
```

```{code-cell} ipython3
Angle((5, 12, 12.23), unit='hourangle')
```

Pueden verse todos los formatos disponibles en [la documentación de astropy](https://docs.astropy.org/en/stable/api/astropy.coordinates.Angle.html)

Usando `Angle` las funciones matemáticas devuelven los resultados correctos:

```{code-cell} ipython3
import numpy as np
np.cos( Angle((60, 0, 0), unit='degree') )
```
