class RK4():
    def __init__(self, func, t0, y0, dt):
        self.func = func
        self.t = t0
        self.y = y0
        self.dt = dt

    def step(self):
        k1 = self.func(self.t,               self.y)
        k2 = self.func(self.t + 0.5*self.dt, self.y + 0.5*k1*self.dt)
        k3 = self.func(self.t + 0.5*self.dt, self.y + 0.5*k2*self.dt)
        k4 = self.func(self.t +     self.dt, self.y +     k3*self.dt)
        self.y += self.dt/6. * (k1 + 2*k2 + 2*k3 + k4)
        self.t += self.dt
