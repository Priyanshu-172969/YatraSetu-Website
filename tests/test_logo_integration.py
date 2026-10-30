"""
test_logo_integration.py - Verification for YatraSetu Authoritative Logo Integration
Covers:
- Presence and preservation of authoritative reference in design-reference/
- Generation and availability of production assets (PNG, SVG, Favicons, Touch Icons)
- Navbar brand integration with two-tone identity (Navy & Terracotta)
- Homepage hero emblem showcase integration
- Footer emblem and brand tagline ('Explore • Plan • Experience')
- HTTP availability of static logo endpoints
"""

import os
import unittest
from app import app


class TestLogoIntegration(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.root_path = app.root_path

    def test_authoritative_reference_files_exist(self):
        """Verifies approved logo reference image is preserved in design-reference/."""
        ref_primary = os.path.join(self.root_path, 'design-reference', 'YatraSetu Heritage Travel Emblem.png')
        ref_photo = os.path.join(self.root_path, 'design-reference', 'design_photo', 'YatraSetu Heritage Travel Emblem.png')
        self.assertTrue(os.path.exists(ref_primary), "Primary reference image must exist in design-reference/")
        self.assertTrue(os.path.exists(ref_photo), "Reference image must exist in design-reference/design_photo/")
        self.assertGreater(os.path.getsize(ref_primary), 500000, "Reference image must be high-resolution")

    def test_production_logo_assets_exist(self):
        """Verifies all static production assets exist and have non-trivial size."""
        required_assets = [
            'images/logo.svg',
            'images/logo.png',
            'images/logo-emblem.png',
            'images/logo-emblem-badge.png',
            'images/favicon.png',
            'images/favicon.ico',
            'images/apple-touch-icon.png',
            'images/hero-emblem.png',
        ]
        for asset in required_assets:
            full_path = os.path.join(self.root_path, 'static', asset)
            self.assertTrue(os.path.exists(full_path), f"Required asset missing: {asset}")
            self.assertGreater(os.path.getsize(full_path), 50, f"Asset too small: {asset}")

    def test_base_template_brand_and_favicon_integration(self):
        """Verifies navbar and footer brand markup in base.html."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')

        # Favicons
        self.assertIn('favicon.ico', html)
        self.assertIn('favicon.png', html)
        self.assertIn('apple-touch-icon.png', html)

        # Navbar Brand
        self.assertIn('brand-logo', html)
        self.assertIn('logo.svg', html)
        self.assertIn('brand-yatra', html)
        self.assertIn('brand-setu', html)
        self.assertIn('Yatra', html)
        self.assertIn('Setu', html)

        # Footer Brand
        self.assertIn('footer-brand-wrap', html)
        self.assertIn('logo-emblem-badge.png', html)
        self.assertIn('Explore • Plan • Experience', html)

    def test_home_page_hero_and_brand_integration(self):
        """Verifies homepage hero section features dominant content focus, clear CTAs, and curated themes."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        res.close()

        self.assertIn('hero-card', html)
        self.assertIn('hero-title', html)
        self.assertTrue("Explore India's Rich Heritage" in html or "Explore India&#39;s Rich Heritage" in html)
        self.assertIn('hero-lead', html)
        self.assertIn('Explore Destinations', html)
        self.assertIn('Compare City Budgets', html)
        self.assertIn('Plan Itineraries', html)
        self.assertIn('Curated Themes', html)

    def test_static_logo_endpoints_return_200(self):
        """Verifies Flask static route successfully serves logo and favicon assets."""
        endpoints = [
            '/static/images/logo.svg',
            '/static/images/logo.png',
            '/static/images/logo-emblem.png',
            '/static/images/logo-emblem-badge.png',
            '/static/images/favicon.png',
            '/static/images/favicon.ico',
            '/static/images/hero-emblem.png',
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Static route failed: {ep}")
            res.close()


if __name__ == '__main__':
    unittest.main()
