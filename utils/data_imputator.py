class ImputeData:
    def __init__(self):
        self.result = {}
        self.pose_items = 33

    def normal_fill(self, body_part):
        landmarks = {'x':[coordinate.x for coordinate in self.detection[body_part][0]],
                     'y':[coordinate.y for coordinate in self.detection[body_part][0]],
                     'z':[coordinate.z for coordinate in self.detection[body_part][0]]}
        
        return landmarks
        
    def previous_hand_fill(self, hand):
        # Indice para obtener las coordenadas de la muñeca derecha o izquierda
        wrist_index = {'r_hand':15, 'l_hand':16}

        # Distancia entre muñeca de la predicción actual y la predicción anterior
        wrist_distances = {'x_dist':self.previous_result[hand][0][0].x - self.detection['pose'][0][wrist_index[hand]].x,
                           'y_dist':self.previous_result[hand][0][0].y - self.detection['pose'][0][wrist_index[hand]].y,
                           'z_dist':self.previous_result[hand][0][0].z - self.detection['pose'][0][wrist_index[hand]].z}
        
        # Coordenadas transladadas a la posición actual de la muñeca
        hand = {'x':[coordinate.x - wrist_distances['x_dist'] for coordinate in self.previous_result[hand][0]],
                'y':[coordinate.y - wrist_distances['y_dist'] for coordinate in self.previous_result[hand][0]],
                'z':[coordinate.z - wrist_distances['z_dist'] for coordinate in self.previous_result[hand][0]]}

        return hand
    
    def not_previous_hand_fill(self, hand):
        # Indices del torso por los cuales reemplazo la mano
        mask = {'r_hand':[15, # Muñeca derecha
                          21, 21, 21, 21, # Pulgar derecho
                          19, 19, 19, 19, # Indice derecho
                          19, 19, 19, 19, # Indice derecho
                          17, 17, 17, 17, # Meñique derecho
                          17, 17, 17, 17], # Meñique derecho
                'l_hand':[16, # Muñeca derecha
                          22, 22, 22, 22, # Pulgar derecho
                          20, 20, 20, 20, # Indice derecho
                          20, 20, 20, 20, # Indice derecho
                          18, 18, 18, 18, # Meñique derecho
                          18, 18, 18, 18]} # Meñique derecho
        
        hand = {'x':[self.detection['pose'][0][i].x for i in mask[hand]],
                'y':[self.detection['pose'][0][i].y for i in mask[hand]],
                'z':[self.detection['pose'][0][i].z for i in mask[hand]]}
        
        return hand

    def pose_fill(self):

        pose ={'x':[None for _ in range(self.pose_items)],
                'y':[None for _ in range(self.pose_items)],
                'z':[None for _ in range(self.pose_items)]}
        
        return pose
        
    def main(self, detection, previous_result):
        
        self.detection = detection
        self.previous_result = previous_result

        if self.detection['r_hand']:
            self.result['r_hand'] = self.normal_fill('r_hand')
        elif not self.detection['r_hand'] and self.previous_result['r_hand']:
            self.result['r_hand'] = self.previous_hand_fill('r_hand')
        else: # No se detecto la mano y no hay datos previos
            self.result['r_hand'] = self.not_previous_hand_fill('r_hand')
        
        if self.detection['l_hand']:
            self.result['l_hand'] = self.normal_fill('l_hand')
        elif not self.detection['l_hand'] and self.previous_result['l_hand']:
            self.result['l_hand'] = self.previous_hand_fill('l_hand')
        else: # No se detecto la mano y no hay datos previos
            self.result['l_hand'] = self.not_previous_hand_fill('l_hand')
        
        if self.detection['pose']:
            self.result['pose'] = self.normal_fill('pose')
        else:
            self.result['pose'] = self.pose_fill()
        
        self.nn_input = []
        for body_part in ['pose', 'r_hand', 'l_hand']:
            for x, y, z in zip(self.result[body_part]['x'], self.result[body_part]['y'], self.result[body_part]['z']):
                self.nn_input.append(x)
                self.nn_input.append(y)
                self.nn_input.append(z)