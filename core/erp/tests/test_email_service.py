from unittest.mock import patch, MagicMock

from core.erp.services.email_service import send_html_email


class TestSendHtmlEmail:
    @patch('core.erp.services.email_service.EmailMessage')
    @patch('core.erp.services.email_service.render_to_string')
    def test_send_html_email_success(self, mock_render, mock_email_cls):
        mock_render.return_value = '<html>Test</html>'
        mock_email = MagicMock()
        mock_email_cls.return_value = mock_email

        result = send_html_email(
            subject='Test Subject',
            template_name='test.html',
            context={'key': 'value'},
            recipient_email='test@example.com',
        )

        assert result is True
        mock_render.assert_called_once_with('test.html', {'key': 'value'})
        mock_email_cls.assert_called_once_with(
            subject='Test Subject',
            body='<html>Test</html>',
            to=['test@example.com'],
        )
        assert mock_email.content_subtype == 'html'
        mock_email.send.assert_called_once_with(fail_silently=False)

    @patch('core.erp.services.email_service.EmailMessage')
    @patch('core.erp.services.email_service.render_to_string')
    def test_send_html_email_failure(self, mock_render, mock_email_cls):
        mock_render.return_value = '<html>Test</html>'
        mock_email = MagicMock()
        mock_email.send.side_effect = Exception('SMTP error')
        mock_email_cls.return_value = mock_email

        result = send_html_email(
            subject='Test',
            template_name='test.html',
            context={},
            recipient_email='test@example.com',
        )

        assert result is False
