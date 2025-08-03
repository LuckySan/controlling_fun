from abc import ABC, abstractmethod

class Controller(ABC):
    """
    Abstract base class for controllers.
    
    This class defines the interface for a controller that computes corrective torque based on the current angle.
    """
    
    @abstractmethod
    def control_torque(self, theta, dt):
        """
        Compute the corrective torque based on the current angle.
        
        Args:
            theta (float): Current angle of the system.
        
        Returns:
            float: Corrective torque to apply.
        """
        pass

class ProportionalController(Controller): 
    """
    A simple proportional controller that calculates the corrective torque based on the angle error from the goal angle.
    
    Attributes:
        K_p (float): Proportional gain for the controller.
    """
    
    def __init__(self, K_p=800.0):
        self.K_p = K_p
    
    def control_torque(self, theta, dt=None):
        """
        Compute the corrective torque based on the angle error.
        
        Args:
            theta (float): Current angle of the system.
        
        Returns:
            float: Corrective torque to apply.
        """
        theta_goal = 0.0 
        theta_error = theta - theta_goal
        tau_corrective = theta_error * self.K_p
        return tau_corrective


class PIController(Controller): 
    """
    A Proportional-Integral controller that calculates the corrective torque based on the angle error and integrates over time.
    
    Attributes:
        K_p (float): Proportional gain for the controller.
        K_i (float): Integral gain for the controller.
        integral (float): Accumulated integral of the angle error.
    """
    
    def __init__(self, K_p=800.0, K_i=50.0):
        self.K_p = K_p
        self.K_i = K_i
        self.integral = 0.0
    
    def control_torque(self, theta, dt):
        """
        Compute the corrective torque based on the angle error and integrate over time.
        
        Args:
            theta (float): Current angle of the system.
            dt (float): Time step for integration.
        
        Returns:
            float: Corrective torque to apply.
        """
        theta_goal = 0.0 
        theta_error = theta - theta_goal
        self.integral += theta_error * dt
        tau_corrective = (theta_error * self.K_p) + (self.integral * self.K_i)
        return tau_corrective


class PIDController(Controller): 
    """
    A Proportional-Integral-Derivative controller that calculates the corrective torque based on the angle error, integrates over time, and considers the derivative of the angle.
    
    Attributes:
        K_p (float): Proportional gain for the controller.
        K_i (float): Integral gain for the controller.
        K_d (float): Derivative gain for the controller.
        integral (float): Accumulated integral of the angle error.
        previous_error (float): Previous angle error for derivative calculation.
    """
    
    def __init__(self, K_p=800.0, K_i=50.0, K_d=10.0):
        self.K_p = K_p
        self.K_i = K_i
        self.K_d = K_d
        self.integral = 0.0
        self.previous_error = 0.0
    
    def control_torque(self, theta, dt):
        """
        Compute the corrective torque based on the angle error, integrate over time, and consider the derivative of the angle.
        
        Args:
            theta (float): Current angle of the system.
            dt (float): Time step for integration.
        
        Returns:
            float: Corrective torque to apply.
        """
        theta_goal = 0.0 
        theta_error = theta - theta_goal
        self.integral += theta_error * dt
        derivative = (theta_error - self.previous_error) / dt if dt > 0 else 0.0
        tau_corrective = (theta_error * self.K_p) + (self.integral * self.K_i) + (derivative * self.K_d)
        self.previous_error = theta_error
        return tau_corrective