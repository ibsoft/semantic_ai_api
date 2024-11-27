using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Newtonsoft.Json;

namespace API_Client
{
    public partial class Form1 : Form
    {
        private static readonly HttpClient client = new HttpClient();
        private Stopwatch stopwatch; // Declare the stopwatch

        public Form1()
        {
            InitializeComponent();
        }

        private async void btnGetToken_Click(object sender, EventArgs e)
        {
            string apiServer = txtApiServer.Text.Trim();
            string username = txtUsername.Text;
            string password = txtPassword.Text;

            // Validate if API Server is provided
            if (string.IsNullOrEmpty(apiServer))
            {
                MessageBox.Show("API server URL is required.");
                return;
            }

            // Login and get the JWT token
            string token = await LoginAsync(apiServer, username, password);
            if (string.IsNullOrEmpty(token))
            {
                MessageBox.Show("Login failed. Please check your credentials.");
                return;
            }

            // Display the token
            txtToken.Text = token;
        }

        private async void btnGetResponse_Click(object sender, EventArgs e)
        {
            string apiServer = txtApiServer.Text.Trim();
            string token = txtToken.Text; // Get token from the TextBox

            if (string.IsNullOrWhiteSpace(token))
            {
                MessageBox.Show("Token is required. Please login first.");
                return;
            }

            // Start the stopwatch to measure the time taken for the response
            stopwatch = Stopwatch.StartNew();

            string result = await GetProtectedResourceAsync(apiServer, token); // Call the updated method

            // Stop the stopwatch once the response is received
            stopwatch.Stop();

            // Display the API response in txtResult
            txtResult.Text = result;

            // Show the elapsed time in the label (in seconds)
            lblElapsedTime.Text = $"Time taken: {stopwatch.ElapsedMilliseconds / 1000.0} seconds";
        }

        private async Task<string> LoginAsync(string apiServer, string username, string password)
        {
            string apiUrl = $"{apiServer}/api/login"; // Using the dynamic API server URL
            var loginData = new
            {
                username = username,
                password = password
            };

            string jsonData = JsonConvert.SerializeObject(loginData);
            var content = new StringContent(jsonData, Encoding.UTF8, "application/json");

            try
            {
                var response = await client.PostAsync(apiUrl, content);
                if (response.IsSuccessStatusCode)
                {
                    var responseString = await response.Content.ReadAsStringAsync();
                    dynamic jsonResponse = JsonConvert.DeserializeObject(responseString);
                    return jsonResponse.access_token; // Adjust based on the API's JSON response format
                }
                else
                {
                    MessageBox.Show($"Login failed: {response.StatusCode}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
                return null;
            }
        }

        private async Task<string> GetProtectedResourceAsync(string apiServer, string token)
        {
            string apiUrl = $"{apiServer}/api/classify"; // Using the dynamic API server URL
            client.DefaultRequestHeaders.Authorization =
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

            var messageData = new
            {
                query = txtMessage.Text.Trim() // Text from txtMessage
            };

            string jsonData = JsonConvert.SerializeObject(messageData);
            var content = new StringContent(jsonData, Encoding.UTF8, "application/json");

            try
            {
                var response = await client.PostAsync(apiUrl, content);
                var responseContent = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    // Beautify JSON before returning
                    var formattedJson = JsonConvert.SerializeObject(JsonConvert.DeserializeObject(responseContent), Formatting.Indented);
                    return formattedJson;
                }
                else
                {
                    return $"Error: {response.StatusCode}\nDetails: {responseContent}";
                }
            }
            catch (Exception ex)
            {
                return $"Error: {ex.Message}";
            }
        }

        private async Task<string> RegisterUserAsync(string apiServer, string username, string password)
        {
            string apiUrl = $"{apiServer}/api/register"; // Using the dynamic API server URL

            var registerData = new
            {
                username = username,
                password = password
            };

            string jsonData = JsonConvert.SerializeObject(registerData);
            var content = new StringContent(jsonData, Encoding.UTF8, "application/json");

            try
            {
                var response = await client.PostAsync(apiUrl, content);
                if (response.IsSuccessStatusCode)
                {
                    return await response.Content.ReadAsStringAsync(); // Return success message
                }
                else
                {
                    MessageBox.Show($"Registration failed: {response.StatusCode}");
                    return null;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
                return null;
            }
        }

        private void buttonClear_Click(object sender, EventArgs e)
        {
            txtMessage.Clear();
        }

        private async void btnStoreMemory_Click(object sender, EventArgs e)
        {
            string token = txtToken.Text;
            string apiServer = txtApiServer.Text;

            // Validate inputs
            if (string.IsNullOrWhiteSpace(token))
            {
                MessageBox.Show("Token is required. Please provide a valid token.");
                return;
            }

            if (string.IsNullOrWhiteSpace(apiServer))
            {
                MessageBox.Show("API server URL is required. Please provide a valid API server.");
                return;
            }

            if (string.IsNullOrWhiteSpace(txtDescription.Text))
            {
                MessageBox.Show("Description is required. Please provide a description.");
                return;
            }

            if (string.IsNullOrWhiteSpace(txtCategory.Text))
            {
                MessageBox.Show("Category is required. Please provide a category.");
                return;
            }

            if (string.IsNullOrWhiteSpace(txtSubCategory.Text))
            {
                MessageBox.Show("Sub-Category is required. Please provide a sub-category.");
                return;
            }

            string apiUrl = $"{apiServer}/api/memory";

            // Construct payload
            var memoryData = new
            {
                Description = txtDescription.Text.Trim(),
                Category = txtCategory.Text.Trim(),
                Subcategory = txtSubCategory.Text.Trim()
            };

            string jsonData = JsonConvert.SerializeObject(memoryData);

            // Debugging: Show payload
            MessageBox.Show($"Payload: {jsonData}");

            var content = new StringContent(jsonData, Encoding.UTF8, "application/json");

            // Add token to headers
            client.DefaultRequestHeaders.Authorization =
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

            try
            {
                var response = await client.PostAsync(apiUrl, content);
                if (response.IsSuccessStatusCode)
                {
                    MessageBox.Show("Memory stored successfully!");
                    // Optionally clear textboxes
                    txtDescription.Clear();
                    txtCategory.Clear();
                    txtSubCategory.Clear();
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    MessageBox.Show($"Error storing memory: {response.StatusCode}\nDetails: {errorContent}");
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
            }
        }

     
    }
}
