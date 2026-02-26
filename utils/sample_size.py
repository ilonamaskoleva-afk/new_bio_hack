import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SampleSizeCalculator:
    """
    Расчет размера выборки для BE исследований
    """
    
    @staticmethod
    def calculate_2x2_crossover(cvintra: float, power: float = 0.80, alpha: float = 0.05, 
                                 theta1: float = 0.80, dropout: float = 0.20) -> dict:
        """
        Расчет для классического 2×2 cross-over дизайна
        
        Args:
            cvintra: Внутрисубъектная вариабельность (в %)
            power: Мощность (обычно 0.80)
            alpha: Уровень значимости (обычно 0.05)
            theta1: Нижняя граница эквивалентности (обычно 0.80)
            dropout: Ожидаемый процент drop-out (в долях, например 0.20 = 20%)
        
        Returns:
            dict с результатами расчета
        """
        
        # Z-scores
        z_alpha = 1.96  # для двустороннего alpha = 0.05
        z_beta = 0.842  # для power = 0.80
        
        # Конвертация CV в дисперсию
        cv_decimal = cvintra / 100
        sigma_squared = math.log(cv_decimal**2 + 1)
        
        # Логарифм границы эквивалентности
        ln_theta1 = math.log(theta1)
        
        # Базовая формула
        numerator = 2 * ((z_alpha + z_beta) ** 2) * sigma_squared
        denominator = ln_theta1 ** 2
        
        n_base = numerator / denominator
        n_base = math.ceil(n_base)  # Округляем вверх
        
        # Корректировка на drop-out
        n_adjusted = n_base / (1 - dropout)
        n_final = math.ceil(n_adjusted)
        
        # Округляем до четного числа (для 2×2 дизайна)
        if n_final % 2 != 0:
            n_final += 1
        
        logger.info(f"Расчет выборки: CV={cvintra}%, базовый N={n_base}, итоговый N={n_final}")
        
        return {
            "design": "2×2 Cross-over",
            "cvintra": cvintra,
            "base_sample_size": n_base,
            "dropout_rate": dropout * 100,
            "adjusted_sample_size": n_adjusted,
            "final_sample_size": n_final,
            "power": power,
            "alpha": alpha,
            "calculation_formula": "N = 2(Zα + Zβ)² × σ² / (ln θ₁)²",
            "steps": [
                f"1. σ² = ln(CV² + 1) = ln({cv_decimal}² + 1) = {sigma_squared:.4f}",
                f"2. ln(θ₁) = ln({theta1}) = {ln_theta1:.4f}",
                f"3. N_base = 2 × ({z_alpha} + {z_beta})² × {sigma_squared:.4f} / {ln_theta1:.4f}² = {n_base}",
                f"4. N_adjusted = {n_base} / (1 - {dropout}) = {n_adjusted:.1f}",
                f"5. N_final (округлено до четного) = {n_final}"
            ]
        }
    
    @staticmethod
    def calculate_replicate(cvintra: float, periods: int = 4, power: float = 0.80, 
                           alpha: float = 0.05, dropout: float = 0.20) -> dict:
        """
        Расчет для replicate дизайна (3-way или 4-way)
        """
        
        # Для replicate дизайна можно использовать меньшую выборку
        # из-за повторных измерений
        
        z_alpha = 1.96
        z_beta = 0.842
        
        cv_decimal = cvintra / 100
        sigma_squared = math.log(cv_decimal**2 + 1)
        
        # Корректировка для replicate (упрощенная формула)
        # В реальности используются более сложные методы
        correction_factor = math.sqrt(periods / 2)
        
        n_base = (2 * ((z_alpha + z_beta) ** 2) * sigma_squared) / ((math.log(0.8)) ** 2)
        n_base = n_base / correction_factor
        n_base = math.ceil(n_base)
        
        n_adjusted = n_base / (1 - dropout)
        n_final = math.ceil(n_adjusted)
        
        # Округляем до кратного периодам
        remainder = n_final % periods
        if remainder != 0:
            n_final += (periods - remainder)
        
        design_name = "3-way Replicate" if periods == 3 else "4-way Replicate"
        
        return {
            "design": design_name,
            "cvintra": cvintra,
            "periods": periods,
            "base_sample_size": n_base,
            "dropout_rate": dropout * 100,
            "adjusted_sample_size": n_adjusted,
            "final_sample_size": n_final,
            "power": power,
            "alpha": alpha,
            "calculation_formula": f"Replicate design with {periods} periods",
            "steps": [
                f"1. σ² = ln(CV² + 1) = {sigma_squared:.4f}",
                f"2. Correction factor for {periods} periods = {correction_factor:.2f}",
                f"3. N_base = {n_base}",
                f"4. N_adjusted for {dropout*100}% dropout = {n_adjusted:.1f}",
                f"5. N_final (округлено до кратного {periods}) = {n_final}"
            ]
        }
    
    @staticmethod
    def recommend_design(cvintra: float) -> dict:
        """
        Рекомендация дизайна на основе CVintra
        """
        
        if cvintra <= 30:
            design = "2×2 Cross-over"
            calculation = SampleSizeCalculator.calculate_2x2_crossover(cvintra)
        elif 30 < cvintra <= 50:
            design = "3-way Replicate"
            calculation = SampleSizeCalculator.calculate_replicate(cvintra, periods=3)
        else:  # > 50%
            design = "4-way Replicate (RSABE)"
            calculation = SampleSizeCalculator.calculate_replicate(cvintra, periods=4)
        
        return {
            "recommended_design": design,
            "rationale": f"CV={cvintra}% → {design} is optimal",
            **calculation
        }