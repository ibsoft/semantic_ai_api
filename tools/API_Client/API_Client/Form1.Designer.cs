namespace API_Client
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            btnGetToken = new Button();
            btnGetResponse = new Button();
            txtUsername = new TextBox();
            txtPassword = new TextBox();
            txtToken = new TextBox();
            txtResult = new TextBox();
            chkRegister = new CheckBox();
            txtMessage = new TextBox();
            label1 = new Label();
            label2 = new Label();
            label3 = new Label();
            btnRegister = new Button();
            label4 = new Label();
            label5 = new Label();
            txtApiServer = new TextBox();
            label6 = new Label();
            lblElapsedTime = new Label();
            buttonClear = new Button();
            pictureBox1 = new PictureBox();
            btnStoreMemory = new Button();
            txtCategory = new TextBox();
            txtSubCategory = new TextBox();
            txtDescription = new TextBox();
            label7 = new Label();
            label8 = new Label();
            label9 = new Label();
            label10 = new Label();
            label11 = new Label();
            label12 = new Label();
            ((System.ComponentModel.ISupportInitialize)pictureBox1).BeginInit();
            SuspendLayout();
            // 
            // btnGetToken
            // 
            btnGetToken.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnGetToken.Location = new Point(942, 240);
            btnGetToken.Name = "btnGetToken";
            btnGetToken.Size = new Size(100, 30);
            btnGetToken.TabIndex = 0;
            btnGetToken.Text = "Get Token";
            btnGetToken.UseVisualStyleBackColor = true;
            btnGetToken.Click += btnGetToken_Click;
            // 
            // btnGetResponse
            // 
            btnGetResponse.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnGetResponse.Location = new Point(940, 595);
            btnGetResponse.Name = "btnGetResponse";
            btnGetResponse.Size = new Size(102, 30);
            btnGetResponse.TabIndex = 1;
            btnGetResponse.Text = "Get";
            btnGetResponse.UseVisualStyleBackColor = true;
            btnGetResponse.Click += btnGetResponse_Click;
            // 
            // txtUsername
            // 
            txtUsername.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            txtUsername.Location = new Point(133, 78);
            txtUsername.Name = "txtUsername";
            txtUsername.PlaceholderText = "Username";
            txtUsername.Size = new Size(702, 27);
            txtUsername.TabIndex = 2;
            txtUsername.Text = "demo";
            // 
            // txtPassword
            // 
            txtPassword.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            txtPassword.Location = new Point(133, 120);
            txtPassword.Name = "txtPassword";
            txtPassword.PasswordChar = '*';
            txtPassword.PlaceholderText = "Password";
            txtPassword.Size = new Size(702, 27);
            txtPassword.TabIndex = 3;
            txtPassword.Text = "demo";
            // 
            // txtToken
            // 
            txtToken.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtToken.Location = new Point(28, 214);
            txtToken.Multiline = true;
            txtToken.Name = "txtToken";
            txtToken.PlaceholderText = "JWT Token";
            txtToken.ReadOnly = true;
            txtToken.Size = new Size(807, 85);
            txtToken.TabIndex = 4;
            // 
            // txtResult
            // 
            txtResult.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtResult.Location = new Point(28, 524);
            txtResult.Multiline = true;
            txtResult.Name = "txtResult";
            txtResult.PlaceholderText = "API Response";
            txtResult.ReadOnly = true;
            txtResult.Size = new Size(807, 173);
            txtResult.TabIndex = 5;
            // 
            // chkRegister
            // 
            chkRegister.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            chkRegister.AutoSize = true;
            chkRegister.Location = new Point(849, 123);
            chkRegister.Name = "chkRegister";
            chkRegister.Size = new Size(85, 24);
            chkRegister.TabIndex = 6;
            chkRegister.Text = "Register";
            chkRegister.UseVisualStyleBackColor = true;
            // 
            // txtMessage
            // 
            txtMessage.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtMessage.Location = new Point(30, 347);
            txtMessage.Multiline = true;
            txtMessage.Name = "txtMessage";
            txtMessage.PlaceholderText = "JWT Token";
            txtMessage.Size = new Size(805, 132);
            txtMessage.TabIndex = 7;
            txtMessage.Text = resources.GetString("txtMessage.Text");
            // 
            // label1
            // 
            label1.AutoSize = true;
            label1.Location = new Point(28, 196);
            label1.Name = "label1";
            label1.Size = new Size(51, 20);
            label1.TabIndex = 8;
            label1.Text = "Token:";
            // 
            // label2
            // 
            label2.AutoSize = true;
            label2.Location = new Point(28, 308);
            label2.Name = "label2";
            label2.Size = new Size(139, 20);
            label2.TabIndex = 9;
            label2.Text = "Message to classify:";
            // 
            // label3
            // 
            label3.AutoSize = true;
            label3.Location = new Point(28, 496);
            label3.Name = "label3";
            label3.Size = new Size(140, 20);
            label3.TabIndex = 10;
            label3.Text = "AI Model Response:";
            // 
            // btnRegister
            // 
            btnRegister.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnRegister.Location = new Point(940, 118);
            btnRegister.Name = "btnRegister";
            btnRegister.Size = new Size(100, 31);
            btnRegister.TabIndex = 11;
            btnRegister.Text = "Register";
            btnRegister.UseVisualStyleBackColor = true;
            // 
            // label4
            // 
            label4.AutoSize = true;
            label4.Location = new Point(28, 121);
            label4.Name = "label4";
            label4.Size = new Size(99, 20);
            label4.TabIndex = 12;
            label4.Text = "API Password:";
            // 
            // label5
            // 
            label5.AutoSize = true;
            label5.Location = new Point(28, 84);
            label5.Name = "label5";
            label5.Size = new Size(108, 20);
            label5.TabIndex = 13;
            label5.Text = "API User name:";
            // 
            // txtApiServer
            // 
            txtApiServer.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            txtApiServer.Location = new Point(133, 29);
            txtApiServer.Name = "txtApiServer";
            txtApiServer.Size = new Size(702, 27);
            txtApiServer.TabIndex = 14;
            txtApiServer.Text = "http://localhost:5000";
            // 
            // label6
            // 
            label6.AutoSize = true;
            label6.Location = new Point(28, 32);
            label6.Name = "label6";
            label6.Size = new Size(93, 20);
            label6.TabIndex = 15;
            label6.Text = "API Provider:";
            // 
            // lblElapsedTime
            // 
            lblElapsedTime.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Right;
            lblElapsedTime.AutoSize = true;
            lblElapsedTime.Location = new Point(858, 677);
            lblElapsedTime.Name = "lblElapsedTime";
            lblElapsedTime.Size = new Size(18, 20);
            lblElapsedTime.TabIndex = 17;
            lblElapsedTime.Text = "...";
            // 
            // buttonClear
            // 
            buttonClear.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            buttonClear.Location = new Point(942, 396);
            buttonClear.Name = "buttonClear";
            buttonClear.Size = new Size(98, 30);
            buttonClear.TabIndex = 18;
            buttonClear.Text = "&Clear";
            buttonClear.UseVisualStyleBackColor = true;
            buttonClear.Click += buttonClear_Click;
            // 
            // pictureBox1
            // 
            pictureBox1.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            pictureBox1.Image = (Image)resources.GetObject("pictureBox1.Image");
            pictureBox1.Location = new Point(959, 32);
            pictureBox1.Name = "pictureBox1";
            pictureBox1.Size = new Size(71, 50);
            pictureBox1.SizeMode = PictureBoxSizeMode.Zoom;
            pictureBox1.TabIndex = 19;
            pictureBox1.TabStop = false;
            // 
            // btnStoreMemory
            // 
            btnStoreMemory.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            btnStoreMemory.Location = new Point(944, 889);
            btnStoreMemory.Name = "btnStoreMemory";
            btnStoreMemory.Size = new Size(98, 32);
            btnStoreMemory.TabIndex = 20;
            btnStoreMemory.Text = "Memory";
            btnStoreMemory.UseVisualStyleBackColor = true;
            btnStoreMemory.Click += btnStoreMemory_Click;
            // 
            // txtCategory
            // 
            txtCategory.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtCategory.Location = new Point(139, 719);
            txtCategory.Name = "txtCategory";
            txtCategory.Size = new Size(696, 27);
            txtCategory.TabIndex = 21;
            // 
            // txtSubCategory
            // 
            txtSubCategory.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            txtSubCategory.Location = new Point(139, 758);
            txtSubCategory.Name = "txtSubCategory";
            txtSubCategory.Size = new Size(696, 27);
            txtSubCategory.TabIndex = 22;
            // 
            // txtDescription
            // 
            txtDescription.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            txtDescription.Location = new Point(139, 796);
            txtDescription.Multiline = true;
            txtDescription.Name = "txtDescription";
            txtDescription.Size = new Size(696, 125);
            txtDescription.TabIndex = 23;
            // 
            // label7
            // 
            label7.AutoSize = true;
            label7.Location = new Point(30, 722);
            label7.Name = "label7";
            label7.Size = new Size(72, 20);
            label7.TabIndex = 24;
            label7.Text = "Category:";
            // 
            // label8
            // 
            label8.AutoSize = true;
            label8.Location = new Point(28, 847);
            label8.Name = "label8";
            label8.Size = new Size(88, 20);
            label8.TabIndex = 25;
            label8.Text = "Description:";
            // 
            // label9
            // 
            label9.AutoSize = true;
            label9.Location = new Point(28, 761);
            label9.Name = "label9";
            label9.Size = new Size(103, 20);
            label9.TabIndex = 26;
            label9.Text = "Sub-Category:";
            // 
            // label10
            // 
            label10.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            label10.AutoSize = true;
            label10.Font = new Font("Segoe UI", 28.2F, FontStyle.Bold, GraphicsUnit.Point, 0);
            label10.Location = new Point(867, 226);
            label10.Name = "label10";
            label10.Size = new Size(54, 62);
            label10.TabIndex = 27;
            label10.Text = "1";
            // 
            // label11
            // 
            label11.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            label11.AutoSize = true;
            label11.Font = new Font("Segoe UI", 28.2F, FontStyle.Bold, GraphicsUnit.Point, 0);
            label11.Location = new Point(867, 577);
            label11.Name = "label11";
            label11.Size = new Size(54, 62);
            label11.TabIndex = 28;
            label11.Text = "2";
            // 
            // label12
            // 
            label12.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            label12.AutoSize = true;
            label12.Font = new Font("Segoe UI", 28.2F, FontStyle.Bold, GraphicsUnit.Point, 0);
            label12.Location = new Point(867, 765);
            label12.Name = "label12";
            label12.Size = new Size(54, 62);
            label12.TabIndex = 29;
            label12.Text = "3";
            // 
            // Form1
            // 
            ClientSize = new Size(1054, 948);
            Controls.Add(label12);
            Controls.Add(label11);
            Controls.Add(label10);
            Controls.Add(label9);
            Controls.Add(label8);
            Controls.Add(label7);
            Controls.Add(txtDescription);
            Controls.Add(txtSubCategory);
            Controls.Add(txtCategory);
            Controls.Add(btnStoreMemory);
            Controls.Add(pictureBox1);
            Controls.Add(buttonClear);
            Controls.Add(lblElapsedTime);
            Controls.Add(label6);
            Controls.Add(txtApiServer);
            Controls.Add(label5);
            Controls.Add(label4);
            Controls.Add(btnRegister);
            Controls.Add(label3);
            Controls.Add(label2);
            Controls.Add(label1);
            Controls.Add(txtMessage);
            Controls.Add(chkRegister);
            Controls.Add(txtResult);
            Controls.Add(txtToken);
            Controls.Add(txtPassword);
            Controls.Add(txtUsername);
            Controls.Add(btnGetResponse);
            Controls.Add(btnGetToken);
            Name = "Form1";
            StartPosition = FormStartPosition.CenterScreen;
            Text = "API Client - by Ioannis A. Bouhras";
            ((System.ComponentModel.ISupportInitialize)pictureBox1).EndInit();
            ResumeLayout(false);
            PerformLayout();
        }

        private System.Windows.Forms.Button btnGetToken;
        private System.Windows.Forms.Button btnGetResponse;
        private System.Windows.Forms.TextBox txtUsername;
        private System.Windows.Forms.TextBox txtPassword;
        private System.Windows.Forms.TextBox txtToken;
        private System.Windows.Forms.TextBox txtResult;
        private System.Windows.Forms.CheckBox chkRegister;
        private TextBox txtMessage;
        private Label label1;
        private Label label2;
        private Label label3;
        private Button btnRegister;
        private Label label4;
        private Label label5;
        private TextBox txtApiServer;
        private Label label6;
        private Label lblElapsedTime;
        private Button buttonClear;
        private PictureBox pictureBox1;
        private Button btnStoreMemory;
        private TextBox txtCategory;
        private TextBox txtSubCategory;
        private TextBox txtDescription;
        private Label label7;
        private Label label8;
        private Label label9;
        private Label label10;
        private Label label11;
        private Label label12;
    }
}
