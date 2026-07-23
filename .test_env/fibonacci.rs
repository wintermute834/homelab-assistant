#[derive(Clone, Copy)]
struct Matrix {
    m00: u128,
    m01: u128,
    m10: u128,
    m11: u128,
}

impl Matrix {
    fn new(m00: u128, m01: u128, m10: u128, m11: u128) -> Self {
        Matrix { m00, m01, m10, m11 }
    }

    fn mul(&self, other: &Matrix) -> Matrix {
        Matrix::new(
            self.m00 * other.m00 + self.m01 * other.m10,
            self.m00 * other.m01 + self.m01 * other.m11,
            self.m10 * other.m00 + self.m11 * other.m10,
            self.m10 * other.m01 + self.m11 * other.m11,
        )
    }

    fn power(&self, n: u128) -> Matrix {
        if n == 0 { return Matrix::new(1, 0, 0, 1); }
        let half = self.power(n / 2);
        let mut result = half.mul(&half);
        if n % 2 == 1 { result = result.mul(self); }
        result
    }
}

pub fn fib(n: u128) -> u128 {
    let base = Matrix::new(1, 1, 1, 0);
    let result = base.power(n);
    result.m01
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fib_small() {
        assert_eq!(fib(0), 0);
        assert_eq!(fib(1), 1);
        assert_eq!(fib(2), 1);
        assert_eq!(fib(3), 2);
        assert_eq!(fib(4), 3);
        assert_eq!(fib(5), 5);
        assert_eq!(fib(6), 8);
    }

    #[test]
    fn test_fib_large() {
        assert_eq!(fib(100), 354224848179261915075);
        assert_eq!(fib(256), 540509396253533123437862351323692357421611153436330200315368604056864915795901280);
    }

    #[test]
    fn test_fib_max_u128() {
        assert_eq!(fib(93), 12_200_160_415_577_788_352u128);
    }
}
