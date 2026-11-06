class ErrorNegocio(Exception):
    """Error controlado: se devuelve al cliente como JSON con su código HTTP."""

    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
