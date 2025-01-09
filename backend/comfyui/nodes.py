
class VAEEncode:
    def encode(self, vae, pixels):
        t = vae.encode(pixels[:,:,:,:3])
        return ({"samples":t}, )

