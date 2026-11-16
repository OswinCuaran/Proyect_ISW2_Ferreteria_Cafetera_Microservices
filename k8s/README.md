# Manifiestos de Kubernetes

Aquí van los manifiestos para desplegar el sistema en Kubernetes: los Deployments y Services de cada microservicio, los StatefulSets de las bases de datos MySQL con sus volúmenes, el ConfigMap con la configuración, el Secret con las contraseñas y el token interno, y el escalado automático del Gateway y de Inventario.

Solo el API Gateway se expone fuera del clúster, por medio de un Service de tipo NodePort en el puerto 30080.
