"""
Integration tests for code metrics functionality
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.metrics import CodeMetricsAnalyzer


class TestCodeMetricsAnalyzer:
    """Test code metrics analysis functionality"""
    
    def test_metrics_analyzer_init(self):
        """Test CodeMetricsAnalyzer initialization"""
        test_dir = Path("tests/sample_module")
        if not test_dir.exists():
            pytest.skip("Sample module not found")
        
        analyzer = CodeMetricsAnalyzer(str(test_dir))
        assert analyzer.project_path.exists()
    
    def test_metrics_analyzer_invalid_path(self):
        """Test CodeMetricsAnalyzer with invalid path"""
        with pytest.raises(ValueError, match="Path does not exist"):
            CodeMetricsAnalyzer("/nonexistent/path")
    
    def test_analyze_complexity(self):
        """Test complexity analysis"""
        test_dir = Path("tests/sample_module")
        if not test_dir.exists():
            pytest.skip("Sample module not found")
        
        try:
            import radon
        except ImportError:
            pytest.skip("radon not installed")
        
        analyzer = CodeMetricsAnalyzer(str(test_dir))
        results = analyzer.analyze_complexity()
        
        assert "status" in results
        assert "files" in results
        assert "average_complexity" in results
        
        if results["status"] == "success":
            assert isinstance(results["files"], dict)
            assert results["average_complexity"] >= 0.0
            
            print(f"\n✅ Complexity analysis results:")
            print(f"   Files analyzed: {len(results['files'])}")
            print(f"   Average complexity: {results['average_complexity']:.2f}")
    
    def test_compute_code_health_score(self):
        """Test code health score computation"""
        test_dir = Path("tests/sample_module")
        if not test_dir.exists():
            pytest.skip("Sample module not found")
        
        analyzer = CodeMetricsAnalyzer(str(test_dir))
        
        # Test with sample scores
        health = analyzer.compute_code_health_score(
            security_score=85.0,
            coverage_score=80.0
        )
        
        assert "code_health_score" in health
        assert "security_score" in health
        assert "coverage_score" in health
        assert "grade" in health
        
        # Check formula: 0.5 * 85 + 0.5 * 80 = 42.5 + 40 = 82.5
        assert health["code_health_score"] == pytest.approx(82.5, rel=0.01)
        assert health["security_score"] == 85.0
        assert health["coverage_score"] == 80.0
        assert health["grade"] == "B"  # 82.5 is in B range (80-89)
    
    def test_health_score_grades(self):
        """Test health score grade assignments"""
        analyzer = CodeMetricsAnalyzer(str(Path("tests/sample_module")))
        
        # Test grade A (90+)
        health_a = analyzer.compute_code_health_score(95.0, 90.0)
        assert health_a["grade"] == "A"
        
        # Test grade B (80-89)
        health_b = analyzer.compute_code_health_score(85.0, 80.0)
        assert health_b["grade"] == "B"
        
        # Test grade C (70-79)
        health_c = analyzer.compute_code_health_score(75.0, 70.0)
        assert health_c["grade"] == "C"
        
        # Test grade D (60-69)
        health_d = analyzer.compute_code_health_score(65.0, 60.0)
        assert health_d["grade"] == "D"
        
        # Test grade F (<60)
        health_f = analyzer.compute_code_health_score(50.0, 50.0)
        assert health_f["grade"] == "F"
    
    def test_health_score_bounds(self):
        """Test that health scores are bounded correctly"""
        analyzer = CodeMetricsAnalyzer(str(Path("tests/sample_module")))
        
        # Test with out-of-range values
        health = analyzer.compute_code_health_score(
            security_score=150.0,  # Over 100
            coverage_score=80.0
        )
        
        # Should be normalized to 0-100 range
        assert health["security_score"] == 100.0
        assert 0.0 <= health["code_health_score"] <= 100.0


class TestMetricsIntegration:
    """Integration tests for metrics analysis workflow"""
    
    def test_radon_available(self):
        """Test that radon is available"""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "radon", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # radon should be installed
            assert result.returncode == 0 or "radon" in result.stdout.lower()
        except FileNotFoundError:
            pytest.skip("radon not installed")
    
    def test_coverage_available(self):
        """Test that coverage is available"""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "coverage", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.skip("coverage not installed")
    
    def test_full_metrics_analysis(self):
        """Test full metrics analysis on sample module"""
        test_dir = Path("tests/sample_module")
        if not test_dir.exists():
            pytest.skip("Sample module not found")
        
        try:
            import radon
        except ImportError:
            pytest.skip("radon not installed")
        
        analyzer = CodeMetricsAnalyzer(str(test_dir))
        
        # Run complexity analysis
        complexity = analyzer.analyze_complexity()
        assert complexity["status"] in ["success", "error"]
        
        if complexity["status"] == "success":
            print(f"\n✅ Full metrics analysis:")
            print(f"   Complexity: {complexity.get('average_complexity', 0):.2f}")
